from collections import OrderedDict
from datetime import timedelta
from pathlib import Path, PurePath

from cached_property import cached_property


COVERS_RELATIVE_PATH = "BDMV/META/DL"
PLAYLISTS_RELATIVE_PATH = "BDMV/PLAYLIST"


class BlurayAnalyzer:
    """Bluray discs analyzer using Ffprobe and Mkvmerge command-line tools.

    :param ffprobe_controller:
        interface with Ffprobe, instance of subclass of
        :class:`~blu_mkv.ffprobe.AbstractFfprobeController`
    :param mkvmerge_controller:
        interface with Ffprobe, instance of subclass of
        :class:`~blu_mkv.mkvmerge.AbstractMkvmergeController`
    """
    def __init__(self, ffprobe_controller, mkvmerge_controller):
        self.ffprobe = ffprobe_controller
        self.mkvmerge = mkvmerge_controller

    def get_playlists(self, disc_path):
        """Return details of playlists present on a Bluray disc by using
        Ffprobe.

        Details are dictionaries with the following keys:
        - duration: playlist duration, instance of :class:`datetime.timedelta`,
        - size: ``int``, playlist size in octets.

        :param str disc_path: path of the Bluray disc
        :return: a dictionary of found playlists, with their number as key
        :return type: dict
        """
        ffprobe_analysis = self.ffprobe.get_bluray_playlists(disc_path)

        playlists = dict()
        for playlist_number, playlist_info in ffprobe_analysis.items():
            playlist_duration = float(playlist_info['duration'])

            playlists[playlist_number] = {
                'bit_rate': int(playlist_info['bit_rate']),
                'duration': timedelta(seconds=playlist_duration),
                'size': int(playlist_info['size'])}

        return playlists

    def get_covers(self, disc_path):
        """Return covers present on a Bluray disc.

        Each cover is a dictionary with the following keys:
        - path: `str`, cover's absolute path,
        - size: `int`, cover's size in bytes.

        :param str disc_path: path of the Bluray disc
        :return: list of found covers
        """
        covers_path = Path(disc_path, COVERS_RELATIVE_PATH)
        return [{
            'path': str(found_cover),
            'size': found_cover.stat().st_size,
        } for found_cover in covers_path.glob('*.jpg')]

    def get_playlist_tracks(self, disc_path, playlist_number):
        """Return tracks' details of a specific Bluray disc's playlist
        by using Ffprobe and Mkvmerge.

        All tracks have the following details:
        - language_code: `str`, language of the track if defined;
                         `None` otherwise

        :param str disc_path: path of the Bluray disc
        :param int playlist_number: playlist's number
        :return: a dictionary of playlist's tracks. Each track is accessible
                 through its type (video, audio or subtitle) and identifier.
        :return type: dict
        """
        playlist_tracks = self._get_all_tracks(disc_path, playlist_number)
        self._set_tracks_languages(disc_path, playlist_number, playlist_tracks)
        return playlist_tracks

    def _get_all_tracks(self, disc_path, playlist_number):
        """Get all tracks of a playlist by using Ffprobe.

        Among all tracks information provided by Ffprobe, only tracks'
        identifiers and types are kept, as other data is not used.
        """
        ffprobe_analysis = (
            self.ffprobe
            .get_all_bluray_playlist_streams(disc_path, playlist_number))

        tracks = {
            'audio': dict(),
            'subtitle': dict(),
            'video': dict()}

        for track in ffprobe_analysis:
            track_id = track['index']
            track_type = track['codec_type']
            tracks[track_type][track_id] = dict()

        return tracks

    def _set_tracks_languages(
            self, disc_path, playlist_number, playlist_tracks):
        """Set all tracks language by using Mkvmerge."""
        playlist_path = PurePath(
            disc_path,
            PLAYLISTS_RELATIVE_PATH,
            '{:05d}.mpls'.format(playlist_number))

        mkvmerge_analysis = self.mkvmerge.get_file_info(str(playlist_path))

        tracks_language = {
            track['id']: track['properties'].get('language')
            for track in mkvmerge_analysis['tracks']}

        for tracks in playlist_tracks.values():
            for track_id, track_info in tracks.items():
                track_info['language_code'] = tracks_language[track_id]

    def get_subtitles_frames_count(self, disc_path, playlist_number):
        """Get subtitles' frames count by using Ffprobe.

        Useful to identify forced subtitles.

        :param str disc_path: path of the Bluray disc
        :param int playlist_number: playlist's number
        :return: a dictionary with subtitle tracks' identifiers as keys,
                 and frames counts as values
        :return type: dict
        """
        ffprobe_analysis = (
            self.ffprobe
            .get_bluray_playlist_subtitles_with_frames_count(
                disc_path, playlist_number))

        subtitles = dict()
        for subtitle in ffprobe_analysis:
            track_id = subtitle['index']
            frames_count = int(subtitle['nb_read_frames'])
            subtitles[track_id] = frames_count

        return subtitles


class BlurayDisc:
    """Bluray disc representation.

    Disc's items are accessed in a lazy fashion as such operations can be
    time-consuming (like probing playlists).

    :param path str: path of the disc
    :param bluray_analyzer: used to lazily probe the disc,
                            instance of :class:`.BlurayAnalyzer`
    """
    def __init__(self, path, bluray_analyzer):
        self.path = path
        self.bluray_analyzer = bluray_analyzer

    @cached_property
    def playlists(self):
        """Return the disc's playlists, sorted by number.

        Each playlist is an instance of :class:`.BlurayPlaylist`.

        :rtype: list
        """
        raw_playlists = self.bluray_analyzer.get_playlists(self.path)

        playlists = list()
        for (playlist_number, playlist_info) in raw_playlists.items():
            playlist = BlurayPlaylist(
                disc=self,
                number=playlist_number,
                duration=playlist_info['duration'],
                size=playlist_info['size'],
                bit_rate=playlist_info['bit_rate'])
            playlists.append(playlist)

        return sorted(playlists, key=lambda playlist: playlist.number)

    @cached_property
    def covers(self):
        """Return the disc's covers.

        See :meth:`.BlurayAnalyzer.get_covers` for more information about
        available covers' details.

        :rtype: list
        """
        return self.bluray_analyzer.get_covers(self.path)

    def get_movie_playlists(self, duration_factor=0.4):
        """Return the disc's movie playlists (e.g. director's cut, special
        edition, extended version, etc.).

        Movie playlists are usually longer than other playlists like bonuses.
        They are thus identified by applying a factor on the duration of the
        longest disc's playlist. All playlists which are longer than the result
        of this multiplication are considered as movie playlists.

        :param float duration_factor: used to identify movie playlists
        :rtype: list
        """
        longest_playlist = max(
            self.playlists, key=lambda playlist: playlist.duration)
        duration_limit = duration_factor * longest_playlist.duration

        return [playlist for playlist in self.playlists
                if playlist.duration >= duration_limit]

    def get_biggest_cover(self):
        """Return the biggest cover of the disc.

        The biggest cover is differentiated from other covers in terms of file
        size and not cover's dimensions.

        :return: the biggest cover if the disc have covers, `None` otherwise
        :rtype: dict or None
        """
        sorted_covers = sorted(
            self.covers, key=lambda cover: cover['size'], reverse=True)

        try:
            return sorted_covers[0]
        except IndexError:
            return None


class BlurayPlaylist:
    """Bluray playlist representation.

    Playlist's items are accessed in a lazy fashion as such operations can be
    time-consuming (like identifying forced subtitles).

    For more information about the available tracks' details of the playlist,
    see :meth:`.BlurayAnalyzer.get_playlist_tracks`.

    :param disc: Bluray disc containing the playlist,
                 instance of :class:`.BlurayDisc`
    :param int number: playlist identifier on the Bluray disc
    :param duration: playlist's duration,
                     instance of :class:`~datetime.timedelta`
    """
    def __init__(self, disc, number, duration, size, bit_rate):
        self.disc = disc
        self.number = number
        self.duration = duration
        self.size = size
        self.bit_rate = bit_rate
        self.path = str(PurePath(
            disc.path, PLAYLISTS_RELATIVE_PATH, "{:05d}.mpls".format(number)))

    def __eq__(self, other):
        return (self.disc == other.disc and
                self.number == other.number and
                self.duration == other.duration and
                self.size == other.size and
                self.bit_rate == other.bit_rate)

    @staticmethod
    def _sort_tracks(tracks):
        """Sort tracks by ID."""
        return OrderedDict(sorted(tracks.items(), key=lambda track: track[0]))

    @cached_property
    def _all_tracks(self):
        """Return all the playlist's tracks."""
        all_tracks = (
            self.disc.bluray_analyzer
            .get_playlist_tracks(self.disc.path, self.number)
            .copy())

        for (track_type, tracks) in all_tracks.items():
            all_tracks[track_type] = self._sort_tracks(tracks)

        return all_tracks

    @property
    def video_tracks(self):
        """Return an ordered dictionary of the playlist's video tracks.

        rtype: instance of :class:`~collections.OrderedDict`
        """
        return self._all_tracks['video']

    @property
    def audio_tracks(self):
        """Return an ordered dictionary of the playlist's audio tracks.

        rtype: instance of :class:`~collections.OrderedDict`
        """
        return self._all_tracks['audio']

    @property
    def subtitle_tracks(self):
        """Return an ordered dictionary of the playlist's subtitle tracks.

        rtype: instance of :class:`~collections.OrderedDict`
        """
        return self._all_tracks['subtitle']

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
        subtitles_frames_count = (
            self.disc.bluray_analyzer
            .get_subtitles_frames_count(self.disc.path, self.number))

        biggest_subtitle = max(subtitles_frames_count.values())
        frames_limit = frames_count_factor * biggest_subtitle

        forced_subtitles = {
            subtitle_id: subtitle_info
            for subtitle_id, subtitle_info in self.subtitle_tracks.items()
            if subtitles_frames_count[subtitle_id] < frames_limit}

        return self._sort_tracks(forced_subtitles)
