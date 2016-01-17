class TestFfprobeController:
    def test_get_default_bluray_playlist_number(self, ffprobe, bluray_dir):
        default_playlist =\
            ffprobe.get_default_bluray_playlist_number(str(bluray_dir))

        assert default_playlist == 419
