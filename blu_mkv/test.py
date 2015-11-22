import textwrap

from .ffprobe import AbstractFfprobeController


class StubFfprobeController(AbstractFfprobeController):
    def get_unformatted_bluray_playlists(self, disc_path):
        return textwrap.dedent("""\
            [bluray @ 0x555da3c70e60] 3 usable playlists:
            [bluray @ 0x555da3c70e60] playlist 00028.mpls (0:07:42)
            [bluray @ 0x555da3c70e60] playlist 00029.mpls (0:05:31)
            [bluray @ 0x555da3c70e60] playlist 00419.mpls (2:23:11)
            [bluray @ 0x555da3c70e60] selected 00419.mpls
            """)

    def get_all_streams_of_bluray_playlist_as_json(
            self, disc_path, playlid_id):
        return {
            'streams': [
                {'index': 0,
                 'codec_type': 'video'},
                {'index': 1,
                 'codec_type': 'audio'},
                {'index': 2,
                 'codec_type': 'audio'},
                {'index': 3,
                 'codec_type': 'subtitle'},
                {'index': 4,
                 'codec_type': 'subtitle'},
                {'index': 5,
                 'codec_type': 'subtitle'}]}

    def get_bluray_playlist_subtitles_with_frames_count_as_json(
            self, disc_path, playlist_id):
        return {
            'streams': [
                {'index': 3,
                 'codec_type': 'subtitle',
                 'nb_read_frames': '2810'},
                {'index': 4,
                 'codec_type': 'subtitle',
                 'nb_read_frames': '18'},
                {'index': 5,
                 'codec_type': 'subtitle',
                 'nb_read_frames': '2680'}]}
