from .ffprobe import AbstractFfprobeController
from .mkvmerge import AbstractMkvmergeController


class StubFfprobeController(AbstractFfprobeController):
    def get_default_bluray_playlist_number(self, disc_path):
        return 419

    def get_bluray_playlists(self, disc_path):
        return {
            28: {'duration': '0:59:59'},
            29: {'duration': '1:00:00'},
            419: {'duration': '2:00:00'}}

    def get_all_bluray_playlist_streams(self, disc_path, playlid_id):
        return [
            {'index': 0, 'codec_type': 'video'},
            {'index': 1, 'codec_type': 'audio'},
            {'index': 2, 'codec_type': 'audio'},
            {'index': 3, 'codec_type': 'subtitle'},
            {'index': 4, 'codec_type': 'subtitle'},
            {'index': 5, 'codec_type': 'subtitle'}]

    def get_bluray_playlist_subtitles_with_frames_count(
            self, disc_path, playlist_id):
        return [
            {'index': 3, 'nb_read_frames': '999'},
            {'index': 4, 'nb_read_frames': '1000'},
            {'index': 5, 'nb_read_frames': '2000'}]


class StubMkvmergeController(AbstractMkvmergeController):
    def get_bluray_playlist_tracks(self, disc_path, playlist_id):
        return {
            0: {
                'type': 'video',
                'codec': 'MPEG-4p10/AVC/h.264',
                'properties': {
                    'pixel_dimensions': '1920x1080',
                    'ts_pid': '4113'}},
            1: {
                'type': 'audio',
                'codec': 'DTS-HD Master Audio',
                'properties': {
                    'audio_channels': '6',
                    'audio_sampling_frequency': '48000',
                    'language': 'fre',
                    'ts_pid': '4352'}},
            2: {
                'type': 'audio',
                'codec': 'DTS-HD Master Audio',
                'properties': {
                    'audio_channels': '6',
                    'audio_sampling_frequency': '48000',
                    'language': 'chi',
                    'ts_pid': '4353'}},
            3: {
                'type': 'subtitles',
                'codec': 'HDMV PGS',
                'properties': {
                    'language': 'fre',
                    'text_subtitles': '1',
                    'ts_pid': '4608'}},
            4: {
                'type': 'subtitles',
                'codec': 'HDMV PGS',
                'properties': {
                    'language': 'fre',
                    'text_subtitles': '1',
                    'ts_pid': '4609'}},
            5: {
                'type': 'subtitles',
                'codec': 'HDMV PGS',
                'properties': {
                    'language': 'chi',
                    'text_subtitles': '1',
                    'ts_pid': '4610'}}}
