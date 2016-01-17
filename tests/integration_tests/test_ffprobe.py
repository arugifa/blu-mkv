import pytest

pytestmark = pytest.mark.ffprobe


class TestFfprobeController:
    def test_get_default_bluray_playlist_number(self, ffprobe, bluray_path):
        default_playlist =\
            ffprobe.get_default_bluray_playlist_number(bluray_path)

        assert isinstance(default_playlist, int)
