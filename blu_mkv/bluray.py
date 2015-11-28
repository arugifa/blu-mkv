from datetime import timedelta
from pathlib import Path


class BlurayAnalyzer:
    """Analyze a Bluray disc by using Ffprobe and Mkvmerge command-line tools.

    :param str disc_path: path of the Bluray disc
    :param ffprobe_controller: interface with Ffprobe
    """
    def __init__(self, disc_path, ffprobe_controller, mkvmerge_controller):
        self.disc_path = disc_path
        self.ffprobe = ffprobe_controller
        self.mkvmerge = mkvmerge_controller

    def get_playlists(self):
        """Return details of playlists present on the Bluray disc by using
        Ffprobe.

        Details are dictionaries with the following keys:
        - duration: playlist duration, instance of :class:`datetime.timedelta`.

        :return: a dictionary of found playlists, with their identifiers
                 as keys
        :return type: dict
        """
        ffprobe_analysis = self.ffprobe.get_bluray_playlists(self.disc_path)

        playlists = dict()
        for playlist_id, playlist_info in ffprobe_analysis.items():
            playlist_duration = [
                int(i) for i in playlist_info['duration'].split(':')]

            playlists[playlist_id] = {
                'duration': timedelta(
                    hours=playlist_duration[0],
                    minutes=playlist_duration[1],
                    seconds=playlist_duration[2]),
            }
        return playlists

    def get_covers(self):
        """Return covers of the Bluray disc.

        Each cover is a dictionary with the following keys:
        - path: `str`, cover's absolute path,
        - size: `int`, cover's size in bytes.

        :return: list of found covers
        """
        covers_path = Path(self.disc_path, 'BDMV/META/DL')
        return [{
            'path': str(found_cover),
            'size': found_cover.stat().st_size,
        } for found_cover in covers_path.glob('*.jpg')]

    def get_playlist_tracks(self, playlist_id):
        """Return tracks' details of a specific playlist by using Ffprobe and
        Mkvmerge.

        All tracks have the following details:
        - language_code: `str`, language of the track if defined;
                         `None` otherwise

        Subtitle tracks have the following additional details:
        - frames_count: `int`, number of frames; useful to identify forced
                        subtitles.

        :param int playlist_id: playlist's identifier
        :return: a dictionary of playlist's tracks. Each track is accessible
                 through its type (video, audio or subtitle) and identifier.
        :return type: dict
        """
        playlist_tracks = self._get_all_tracks(playlist_id)
        self._set_tracks_languages(playlist_id, playlist_tracks)
        self._set_subtitles_frames_count(
            playlist_id, playlist_tracks['subtitle'])

        return playlist_tracks

    def _get_all_tracks(self, playlist_id):
        """Get all tracks of a playlist by using Ffprobe.

        Among all tracks information provided by Ffprobe, only tracks'
        identifier and type are kept, as other data is not used.
        """
        ffprobe_analysis = \
            self.ffprobe \
            .get_all_bluray_playlist_streams(self.disc_path, playlist_id)

        tracks = {
            'audio': dict(),
            'subtitle': dict(),
            'video': dict()}

        for track in ffprobe_analysis:
            track_id = track['index']
            track_type = track['codec_type']
            tracks[track_type][track_id] = dict()

        return tracks

    def _set_tracks_languages(self, playlist_id, playlist_tracks):
        """Set all tracks language by using Mkvmerge."""
        mkvmerge_analysis = \
            self.mkvmerge \
            .get_bluray_playlist_tracks(self.disc_path, playlist_id)

        tracks_language = {
            int(track_id): track_info['properties'].get('language')
            for track_id, track_info in mkvmerge_analysis.items()}

        for tracks in playlist_tracks.values():
            for track_id, track_info in tracks.items():
                track_info['language_code'] = tracks_language[track_id]

    def _set_subtitles_frames_count(self, playlist_id, subtitles):
        """Set subtitles' frames count by using Ffprobe."""
        ffprobe_analysis = self.ffprobe \
                           .get_bluray_playlist_subtitles_with_frames_count(
                               self.disc_path, playlist_id)

        for subtitle in ffprobe_analysis:
            track_id = subtitle['index']
            frames_count = int(subtitle['nb_read_frames'])
            subtitles[track_id]['frames_count'] = frames_count
