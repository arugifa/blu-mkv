import pytest


class TestBlurayAnalyzer:
    @pytest.mark.ffprobe
    def test_get_playlists(self, bluray_analyzer, bluray_path):
        playlists = bluray_analyzer.get_playlists(bluray_path)
        assert len(playlists) > 0

    @pytest.mark.ffprobe
    @pytest.mark.mkvmerge
    def test_get_playlist_tracks(self, bluray_analyzer, bluray_path):
        default_playlist = (
            bluray_analyzer.ffprobe_controller
            .get_default_bluray_playlist_number(bluray_path))

        tracks =\
            bluray_analyzer.get_playlist_tracks(bluray_path, default_playlist)

        for track_type in ['video', 'audio', 'subtitle']:
            assert len(tracks[track_type]) > 0

    @pytest.mark.ffprobe
    def test_get_subtitles_frames_count(self, bluray_analyzer, bluray_path):
        default_playlist = (
            bluray_analyzer.ffprobe_controller
            .get_default_bluray_playlist_number(bluray_path))

        frames_count = (
            bluray_analyzer
            .get_subtitles_frames_count(str(bluray_path), default_playlist))

        assert len(frames_count) > 0

    @pytest.mark.makemkv
    def test_identify_multiview_playlists(self, bluray_analyzer, bluray_path):
        multiview_playlists =\
            bluray_analyzer.identify_multiview_playlists(str(bluray_path))

        assert len(multiview_playlists) > 0
