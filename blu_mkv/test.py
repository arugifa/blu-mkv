import textwrap


class FfprobeStubController:
    def get_unformatted_bluray_playlists(self, disc_path):
        return textwrap.dedent("""\
        [bluray @ 0x555da3c70e60] 3 usable playlists:
        [bluray @ 0x555da3c70e60] playlist 00028.mpls (0:07:42)
        [bluray @ 0x555da3c70e60] playlist 00029.mpls (0:05:31)
        [bluray @ 0x555da3c70e60] playlist 00419.mpls (2:23:11)
        [bluray @ 0x555da3c70e60] selected 00419.mpls
        """)
