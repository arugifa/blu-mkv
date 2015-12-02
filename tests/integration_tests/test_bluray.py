class TestBlurayAnalyzer:
    def test_get_playlists(self, bluray_analyzer, bluray_path):
        playlists = bluray_analyzer.get_playlists(bluray_path)
        assert len(playlists) > 0

    def test_get_playlist_tracks(self, bluray_analyzer, bluray_path):
        default_playlist = bluray_analyzer.ffprobe \
                           .get_default_bluray_playlist_number(bluray_path)

        tracks = bluray_analyzer \
                 .get_playlist_tracks(bluray_path, default_playlist)

        for track_type in ['video', 'audio', 'subtitle']:
            assert len(tracks[track_type]) > 0
