class TestBlurayAnalyzer:
    def test_get_playlists(self, bluray_analyzer):
        playlists = bluray_analyzer.get_playlists()
        assert len(playlists) > 0
