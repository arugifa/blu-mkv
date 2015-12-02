from datetime import timedelta
from pathlib import Path

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
        - duration: playlist duration, instance of :class:`datetime.timedelta`.

        :param str disc_path: path of the Bluray disc
        :return: a dictionary of found playlists, with their number as key
        :return type: dict
        """
        ffprobe_analysis = self.ffprobe.get_bluray_playlists(disc_path)

        playlists = dict()
        for playlist_number, playlist_info in ffprobe_analysis.items():
            playlist_duration = [
                int(i) for i in playlist_info['duration'].split(':')]

            playlists[playlist_number] = {
                'duration': timedelta(
                    hours=playlist_duration[0],
                    minutes=playlist_duration[1],
                    seconds=playlist_duration[2]),
            }
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

        Subtitle tracks have the following additional details:
        - frames_count: `int`, number of frames; useful to identify forced
                        subtitles.

        :param str disc_path: path of the Bluray disc
        :param int playlist_number: playlist's number
        :return: a dictionary of playlist's tracks. Each track is accessible
                 through its type (video, audio or subtitle) and identifier.
        :return type: dict
        """
        playlist_tracks = self._get_all_tracks(disc_path, playlist_number)
        self._set_tracks_languages(disc_path, playlist_number, playlist_tracks)
        self._set_subtitles_frames_count(
            disc_path, playlist_number, playlist_tracks['subtitle'])

        return playlist_tracks

    def _get_all_tracks(self, disc_path, playlist_number):
        """Get all tracks of a playlist by using Ffprobe.

        Among all tracks information provided by Ffprobe, only tracks'
        identifiers and types are kept, as other data is not used.
        """
        ffprobe_analysis = \
            self.ffprobe \
            .get_all_bluray_playlist_streams(disc_path, playlist_number)

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
        mkvmerge_analysis = \
            self.mkvmerge \
            .get_bluray_playlist_tracks(disc_path, playlist_number)

        tracks_language = {
            int(track_id): track_info['properties'].get('language')
            for track_id, track_info in mkvmerge_analysis.items()}

        for tracks in playlist_tracks.values():
            for track_id, track_info in tracks.items():
                track_info['language_code'] = tracks_language[track_id]

    def _set_subtitles_frames_count(
            self, disc_path, playlist_number, subtitles):
        """Set subtitles' frames count by using Ffprobe."""
        ffprobe_analysis = self.ffprobe \
                           .get_bluray_playlist_subtitles_with_frames_count(
                               disc_path, playlist_number)

        for subtitle in ffprobe_analysis:
            track_id = subtitle['index']
            frames_count = int(subtitle['nb_read_frames'])
            subtitles[track_id]['frames_count'] = frames_count
