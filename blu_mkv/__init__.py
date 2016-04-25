from collections import OrderedDict
from datetime import timedelta
from pathlib import PurePath
import subprocess

from cached_property import cached_property

from .ffprobe import FfprobeController
from .mediainfo import MediaInfoController
from .mkvmerge import MkvMergeController


class ProgramController:
    """Base interface with an external program.

    :param str executable_path: absolute path of the program's executable file
    """
    def __init__(self, executable_file):
        """
        :param str executable_file:
            name or absolute path of the program's executable file.
            If a name is given, the related file will be searched in
            the directories listed in the environment variable ``PATH``
        """
        self.executable_path = self._get_executable_path(executable_file)

    @staticmethod
    def _get_executable_path(executable_file):
        """Return the absolute path of the program's executable file."""
        if PurePath(executable_file).is_absolute():
            executable_path = executable_file
        else:
            try:
                which_output = subprocess.check_output(
                    ['which', executable_file],
                    stderr=subprocess.PIPE,
                    universal_newlines=True)
            except subprocess.CalledProcessError as exc:
                error = exc.stderr.rstrip()
                raise FileNotFoundError(error) from exc

            executable_path = which_output.rstrip()

        return executable_path


class MultimediaFileAnalyzer:
    "Blu-ray disc analyzer using the Ffprobe, Mkvmerge and Makemkv programs."
    ffprobe_controller = FfprobeController()
    mediainfo_controller = MediaInfoController()
    mkvmerge_controller = MkvMergeController()

    def count_subtitle_frames(self, file_path):
        """Get subtitles' frames count by using Ffprobe.

        Useful to identify forced subtitles.

        :param str disc_path: path of the Bluray disc. Must points to a
                              directory
        :param int playlist_number: playlist's number
        :return: a dictionary with subtitle tracks' identifiers as keys,
                 and frames counts as values
        :return type: dict
        """
        subtitles_properties =\
            self.ffprobe_controller.count_subtitle_frames(file_path)

        all_frames_count = dict()
        for subtitle in subtitles_properties:
            track_id = subtitle['index']
            frames_count = int(subtitle['nb_read_frames'])
            all_frames_count[track_id] = frames_count

        return all_frames_count

    def get_properties(self, file_path):
        """Return tracks' details of a specific Bluray disc's playlist
        by using Ffprobe and Mkvmerge.

        All tracks have the following details:
        - language_code: `str`, language of the track if defined
                         (in ISO639-2 format); `None` otherwise
        - uid: `int`, unique identifier of the track

        :param str disc_path: path of the Bluray disc. Must points to a
                              directory
        :param int playlist_number: playlist's number
        :return: a dictionary of playlist's tracks. Each track is accessible
                 through its type (video, audio or subtitle) and index (which
                 is different from the track's uid)
        :return type: dict
        """
        file_properties = self._probe_with_mediainfo(file_path)
        container_properties = self._probe_with_ffprobe(file_path)['format']
        tracks_properties = self._probe_with_mkvmerge(file_path)['tracks']

        duration = container_properties.get('duration')
        if duration is not None:
            # Convert playlist duration from nanoseconds to microseconds.
            duration = timedelta(microseconds=duration / 1000)

        tracks = self._format_tracks(tracks_properties)
        self._set_views_count(tracks['video'], file_properties)

        return {
            'duration': duration,
            'size': container_properties['size'],
            'tracks': tracks}

    def _format_tracks(self, raw_tracks):
        tracks = {
            track_type: dict()
            for track_type in ['audio', 'subtitles', 'video']}

        for track in raw_tracks:
            track_id = track['id']
            track_type = track['type']

            tracks[track_type][track_id] = {
                'language_code': track['properties'].get('language'),
                'uid': track['properties']['number']}

        return tracks

    def _probe_with_ffprobe(self, file_path):
        return self.ffprobe_controller.get_file_info(file_path)

    def _probe_with_mediainfo(self, file_path):
        return self.mediainfo_controller.get_file_info(file_path)

    def _probe_with_mkvmerge(self, file_path):
        return self.mkvmerge_controller.get_file_info(file_path)

    def _set_views_count(self, video_tracks, mediainfo_analysis):
        """Return numbers of playlists containing multiview tracks (like
        three-dimensional video tracks) by using Makemkv.

        :param str disc_path: path of the Bluray disc. Must points to a
                              directory
        :return: a list with numbers of multiview playlists
        :return type: list
        :raises AssertionError: if :attr:`.makemkv` is not set (no Makemkv
                                controller defined)
        """
        for track in mediainfo_analysis.xpath('./File/track[@type="Video"]'):
            track_id = int(track.find('ID').text)

            multiview_count = track.find('MultiView_Count')
            if multiview_count is not None:
                views_count = 1
            else:
                views_count = int(multiview_count.text)

            video_tracks[track_id]['views_count'] = views_count


class MultimediaFile:
    """Bluray playlist representation.

    Playlist's items are accessed in a lazy fashion as such operations can be
    time-consuming (like identifying forced subtitles).

    For more information about the available tracks' details of the playlist,
    see :meth:`.BlurayAnalyzer.get_playlist_tracks`.

    :param str path: playlist's path
    """
    analyzer = None

    def __init__(self, path):
        self.path = path

    def __eq__(self, other):
        return (self.size == other.size and
                self.duration == other.duration and
                self.video_tracks == other.video_tracks and
                self.audio_tracks == other.audio_tracks and
                self.subtitle_tracks == other.subtitle_tracks)

    @property
    def audio_tracks(self):
        """Return an ordered dictionary of the playlist's audio tracks.

        High Definition tracks can embed a second track (aka core stream) in
        Simple Definition/lossy format. When this is the case, the SD track is
        discarded.

        rtype: instance of :class:`~collections.OrderedDict`
        """
        all_audio_tracks = self.properties['tracks']['audio']
        filtered_tracks = OrderedDict()

        for (track_id, track_info) in all_audio_tracks.items():
            # Discard SD/lossy tracks, which have the same UID as their
            # relative HD tracks, but a bigger index (track number).
            track_is_lossy = any(
                track_info['uid'] == other_track['uid']
                for other_track in filtered_tracks.values())

            if track_is_lossy:
                continue
            filtered_tracks[track_id] = track_info

        return filtered_tracks

    @property
    def duration(self):
        return self.properties['duration']

    @cached_property
    def properties(self):
        file_properties = self.analyzer.get_properties(self.path)

        playlist_tracks = file_properties['tracks']
        for (track_type, tracks) in playlist_tracks.items():
            playlist_tracks[track_type] = self._sort_tracks(tracks)

        return file_properties

    @property
    def size(self):
        return self.properties['size']

    @property
    def subtitle_tracks(self):
        """Return an ordered dictionary of the playlist's subtitle tracks.

        rtype: instance of :class:`~collections.OrderedDict`
        """
        return self.properties['tracks']['subtitles']

    @property
    def video_tracks(self):
        """Return an ordered dictionary of the playlist's video tracks.

        rtype: instance of :class:`~collections.OrderedDict`
        """
        return self.properties['tracks']['video']

    def get_forced_subtitles(self, frames_count_factor=0.3):
        """Return forced subtitles of the playlist, by computing frames count
        for each subtitle track.

        Forced subtitles have usually less frames than other subtitles.
        They are thus identified by applying a factor on the frames count of
        the "biggest" playlist's subtitle track. All subtitles which have less
        frames than the result of this multiplication are considered as forced
        subtitles.

        Be aware: this is a time-consuming operation!

        :param float frames_count_factor: used to identify forced subtitles
        rtype: instance of :class:`~collections.OrderedDict`
        """
        subtitle_frames_count = self.analyzer.count_subtitle_frames(self.path)

        if not subtitle_frames_count:
            return OrderedDict()

        biggest_subtitle = max(subtitle_frames_count.values())
        frames_limit = frames_count_factor * biggest_subtitle

        forced_subtitles = {
            subtitle_id: subtitle_info
            for subtitle_id, subtitle_info in self.subtitle_tracks.items()
            if subtitle_frames_count[subtitle_id] < frames_limit}

        return self._sort_tracks(forced_subtitles)

    @staticmethod
    def _sort_tracks(tracks):
        """Sort tracks by ID."""
        return OrderedDict(sorted(tracks.items(), key=lambda track: track[0]))
