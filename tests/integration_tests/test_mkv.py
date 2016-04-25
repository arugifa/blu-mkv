import pytest


class TestMkvAnalyzer:
    @pytest.mark.ffprobe
    def test_get_attachments(self, mkv_analyzer, mkv_path):
        attachments = mkv_analyzer.get_attachments(mkv_path)
        assert len(attachments) > 0

    @pytest.mark.ffprobe
    def test_get_title(self, mkv_analyzer, mkv_path):
        title = mkv_analyzer.get_title(mkv_path)
        assert title

    @pytest.mark.ffprobe
    def test_get_tracks(self, mkv_analyzer, mkv_path):
        tracks = mkv_analyzer.get_tracks(mkv_path)

        for track_type in ['video', 'audio', 'subtitle']:
            assert len(tracks[track_type]) > 0
