from datetime import timedelta


class TestBlurayAnalyzer:
    def test_get_playlists(self, bluray_analyzer):
        expected_playlists = [
            {'id': '00028',
             'duration': timedelta(hours=0, minutes=7, seconds=42)},
            {'id': '00029',
             'duration': timedelta(hours=0, minutes=5, seconds=31)},
            {'id': '00419',
             'duration': timedelta(hours=2, minutes=23, seconds=11)}]
        actual_playlists = bluray_analyzer.get_playlists()
        assert actual_playlists == expected_playlists
