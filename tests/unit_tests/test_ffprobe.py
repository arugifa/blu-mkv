class TestAbstractFfprobeController:
    def test_get_default_bluray_playlist(self, ffprobe):
        default_playlist = ffprobe.get_default_bluray_playlist('/tmp/bluray')
        assert default_playlist == '00419'
