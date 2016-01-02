from collections import OrderedDict
from datetime import timedelta

from blu_mkv.bluray import BlurayDisc, BlurayPlaylist


class TestBlurayAnalyzer:
    def test_get_playlists(self, bluray_analyzer, bluray_dir):
        actual_playlists = bluray_analyzer.get_playlists(str(bluray_dir))
        expected_playlists = {
            28: {'duration': timedelta(minutes=59, seconds=59),
                 'size': 16970468350},
            29: {'duration': timedelta(hours=1),
                 'size': 16970468352},
            419: {'duration': timedelta(hours=2),
                  'size': 33940936704}}

        assert actual_playlists == expected_playlists

    def test_get_covers(self, bluray_analyzer, bluray_dir, bluray_covers):
        actual_covers = bluray_analyzer.get_covers(str(bluray_dir))
        expected_covers = [
            {'path': str(cover), 'size': cover.size()}
            for cover in [bluray_covers['big'], bluray_covers['small']]]

        assert actual_covers == expected_covers

    def test_get_playlist_tracks(self, bluray_analyzer, bluray_dir):
        actual_tracks =\
            bluray_analyzer.get_playlist_tracks(str(bluray_dir), 419)

        expected_tracks = {
            'video': {
                0: {'language_code': None}},
            'audio': {
                1: {'language_code': 'fre'},
                2: {'language_code': 'chi'}},
            'subtitle': {
                3: {'language_code': 'fre'},
                4: {'language_code': 'fre'},
                5: {'language_code': 'chi'}}}

        assert actual_tracks == expected_tracks

    def test_get_subtitles_frames_count(self, bluray_analyzer, bluray_dir):
        actual_frames_count =\
            bluray_analyzer.get_subtitles_frames_count(str(bluray_dir), 419)

        expected_frames_count = {3: 999, 4: 1000, 5: 2000}

        assert actual_frames_count == expected_frames_count


class TestBlurayDisc:
    def test_bluray_playlists(self, bluray_disc):
        expected_playlists = [
            BlurayPlaylist(bluray_disc, 28, timedelta(minutes=59, seconds=59)),
            BlurayPlaylist(bluray_disc, 29, timedelta(hours=1)),
            BlurayPlaylist(bluray_disc, 419, timedelta(hours=2))]

        assert bluray_disc.playlists == expected_playlists

    def test_get_movie_playlists(self, bluray_disc):
        actual_movie_playlists =\
            bluray_disc.get_movie_playlists(duration_factor=0.5)

        expected_movie_playlists = [
            BlurayPlaylist(bluray_disc, 29, timedelta(hours=1)),
            BlurayPlaylist(bluray_disc, 419, timedelta(hours=2))]

        assert actual_movie_playlists == expected_movie_playlists

    def test_bluray_covers(self, bluray_disc, bluray_covers):
        expected_covers = [
            {'path': str(cover), 'size': cover.size()}
            for cover in [bluray_covers['big'], bluray_covers['small']]]

        assert bluray_disc.covers == expected_covers

    def test_get_biggest_cover(self, bluray_disc, bluray_covers):
        biggest_cover = bluray_disc.get_biggest_cover()
        assert biggest_cover['path'] == str(bluray_covers['big'])

    def test_get_biggest_cover_when_no_covers_exist(
            self, tmpdir, bluray_analyzer):
        bluray_dir = tmpdir.mkdir('bluray_disc')
        bluray_disc = BlurayDisc(str(bluray_dir), bluray_analyzer)

        biggest_cover = bluray_disc.get_biggest_cover()
        assert biggest_cover is None


class TestBlurayPlaylist:
    def test_video_tracks(self, bluray_playlist):
        actual_video_tracks = bluray_playlist.video_tracks
        expected_video_tracks = OrderedDict([(0, {'language_code': None})])

        assert isinstance(actual_video_tracks, OrderedDict)
        assert actual_video_tracks == expected_video_tracks

    def test_audio_tracks(self, bluray_playlist):
        actual_audio_tracks = bluray_playlist.audio_tracks
        expected_audio_tracks = OrderedDict([
            (1, {'language_code': 'fre'}),
            (2, {'language_code': 'chi'})])

        assert isinstance(actual_audio_tracks, OrderedDict)
        assert actual_audio_tracks == expected_audio_tracks

    def test_subtitle_tracks(self, bluray_playlist):
        actual_subtitle_tracks = bluray_playlist.subtitle_tracks
        expected_subtitle_tracks = OrderedDict([
            (3, {'language_code': 'fre'}),
            (4, {'language_code': 'fre'}),
            (5, {'language_code': 'chi'})])

        assert isinstance(actual_subtitle_tracks, OrderedDict)
        assert actual_subtitle_tracks == expected_subtitle_tracks

    def test_get_forced_subtitles(self, bluray_playlist):
        actual_forced_subtitles =\
            bluray_playlist.get_forced_subtitles(frames_count_factor=0.5)

        expected_forced_subtitles =\
            OrderedDict([(3, {'language_code': 'fre'})])

        assert isinstance(actual_forced_subtitles, OrderedDict)
        assert actual_forced_subtitles == expected_forced_subtitles
