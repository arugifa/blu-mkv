from datetime import timedelta


class TestBlurayAnalyzer:
    def test_get_playlists(self, bluray_analyzer, bluray_dir):
        expected_playlists = {
            28: {'duration': timedelta(hours=0, minutes=7, seconds=42)},
            29: {'duration': timedelta(hours=0, minutes=5, seconds=31)},
            419: {'duration': timedelta(hours=2, minutes=23, seconds=11)}}
        actual_playlists = bluray_analyzer.get_playlists(str(bluray_dir))
        assert actual_playlists == expected_playlists

    def test_get_covers(self, bluray_analyzer, bluray_dir, bluray_covers):
        expected_covers = [{'path': str(cover), 'size': cover.size()}
                           for cover in bluray_covers]
        actual_covers = bluray_analyzer.get_covers(str(bluray_dir))
        assert actual_covers == expected_covers

    def test_get_playlist_tracks(self, bluray_analyzer, bluray_dir):
        expected_tracks = {
            'video': {
                0: {'language_code': None}},
            'audio': {
                1: {'language_code': 'fre'},
                2: {'language_code': 'chi'}},
            'subtitle': {
                3: {'language_code': 'fre', 'frames_count': 2810},
                4: {'language_code': 'fre', 'frames_count': 18},
                5: {'language_code': 'chi', 'frames_count': 2680}}}
        actual_tracks = bluray_analyzer \
                        .get_playlist_tracks(str(bluray_dir), 419)
        assert actual_tracks == expected_tracks
