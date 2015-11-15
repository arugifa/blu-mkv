import re


class TestFfprobeController:
    def test_get_unformatted_bluray_playlists(self, ffprobe, bluray_path):
        assert re.search(
            r'\[bluray @ 0x\w+] playlist \d+.mpls \(\d+:\d{2}:\d{2}\)',
            ffprobe.get_unformatted_bluray_playlists(bluray_path))
