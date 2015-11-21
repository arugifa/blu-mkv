class TestFfprobeController:
    def test_get_unformatted_bluray_playlists(self, ffprobe, bluray_path):
        ffprobe_output = ffprobe.get_unformatted_bluray_playlists(bluray_path)
        assert ffprobe_output != ''
