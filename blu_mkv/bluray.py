from datetime import timedelta
from pathlib import Path
import re


class BlurayAnalyzer:
    """Analyze a Bluray disc by using Ffprobe and Mkvmerge command-line tools.

    :param str disc_path: path of the Bluray disc.
    :param ffprobe_controller: interface with Ffprobe.
    """
    def __init__(self, disc_path, ffprobe_controller, mkvmerge_controller):
        self.disc_path = disc_path
        self.ffprobe = ffprobe_controller
        self.mkvmerge = mkvmerge_controller

    def get_playlists(self):
        """Return Bluray disc's playlists by using Ffprobe.

        Each playlist is a dictionary with the following details:
        - id: playlist's identifier as a string,
        - duration: playlist's duration, instance of
                    :class:`datetime.timedelta`.

        :return: list of found playlists.
        """
        playlists_details = re.findall(
            r'playlist (\d+)\.mpls \((\d+:\d{2}:\d{2})\)',
            self.ffprobe.get_unformatted_bluray_playlists(self.disc_path))

        playlists = list()
        for playlist in playlists_details:
            playlist_duration = [int(i) for i in playlist[1].split(':')]
            playlists.append({
                'id': playlist[0],
                'duration': timedelta(
                    hours=playlist_duration[0],
                    minutes=playlist_duration[1],
                    seconds=playlist_duration[2]),
            })
        return playlists

    def get_covers(self):
        """Return Bluray disc's covers.

        Each cover is a dictionary with the following details:
        - path: cover's absolute path,
        - size: cover's size in bytes.

        :return: list of found covers.
        """
        covers_path = Path(self.disc_path, 'BDMV/META/DL')
        return [{
            'path': str(found_cover),
            'size': found_cover.stat().st_size,
        } for found_cover in covers_path.glob('*.jpg')]

    def get_playlist_tracks(self, playlist_id):
        """Return all tracks of a specific playlist by using Ffprobe and
        Mkvmerge.

        Tracks are organized by type (video, audio or subtitle) and have the
        following details:
        - language_code: str, language of the track if defined; None otherwise.

        Subtitles have the following additional details:
        - frames_count: int, number of frames; useful to identify forced
                        subtitles.

        :param str playlist_id: playlist's identifier
        :return: playlist's tracks. Each track is accessible through its type
                 and identifier.
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
        ffprobe_output = \
            self.ffprobe \
            .get_all_streams_of_bluray_playlist_as_json(
                self.disc_path, playlist_id) \
            ['streams']

        all_tracks = {
            'audio': dict(),
            'subtitle': dict(),
            'video': dict()}

        for track in ffprobe_output:
            track_id = track['index']
            track_type = track['codec_type']
            all_tracks[track_type][track_id] = dict()

        return all_tracks

    def _set_tracks_languages(self, playlist_id, playlist_tracks):
        """Set all tracks language by using Mkvmerge."""
        mkvmerge_output = re.findall(
            r'Track ID (\d+): (\w+) \(.+\) \[.*(language:(\w{3})).*\]',
            self.mkvmerge.get_all_tracks_of_bluray_playlist(
                self.disc_path, playlist_id))

        tracks_language = {
            int(track[0]): track[3]
            for track in mkvmerge_output}

        for tracks in playlist_tracks.values():
            for track_id, track_info in tracks.items():
                track_info['language_code'] = tracks_language.get(track_id)

    def _set_subtitles_frames_count(self, playlist_id, subtitles):
        """Set subtitles' frames count by using Ffprobe."""
        ffprobe_output = \
            self.ffprobe \
            .get_bluray_playlist_subtitles_with_frames_count_as_json(
                self.disc_path, playlist_id) \
            ['streams']

        for subtitle in ffprobe_output:
            track_id = subtitle['index']
            frames_count = int(subtitle['nb_read_frames'])
            subtitles[track_id]['frames_count'] = frames_count
