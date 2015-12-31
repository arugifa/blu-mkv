from collections import OrderedDict

from blu_mkv import helpers

tracks = OrderedDict([
    (0, {'language': 'chi'}),
    (1, {'language': 'fre', 'codec': 'SRT'}),
    (2, {'language': 'fre', 'codec': 'PGS'}),
    (3, {'language': 'fre', 'codec': 'PGS'})])


class TestFilterTracks:
    def test_do_not_use_filters(self):
        selected_tracks = helpers.filter_tracks(tracks)
        assert selected_tracks is tracks

    def test_use_filters(self):
        actual_selected_tracks =\
            helpers.filter_tracks(tracks, language='fre', codec='PGS')
        expected_selected_tracks = OrderedDict([
            (track_id, tracks[track_id]) for track_id in [2, 3]])

        assert isinstance(actual_selected_tracks, OrderedDict)
        assert actual_selected_tracks == expected_selected_tracks


class TestSortTracks:
    def test_only_sort_by_tracks_identifier(self):
        tracks = {track_id: {} for track_id in [2, 1, 0]}
        actual_sorted_tracks = helpers.sort_tracks(tracks)
        expected_sorted_tracks = OrderedDict(sorted(tracks.items()))

        assert isinstance(actual_sorted_tracks, OrderedDict)
        assert actual_sorted_tracks == expected_sorted_tracks

    def test_sort_by_tracks_properties_and_identifier(self):
        actual_sorted_tracks =\
            helpers.sort_tracks(tracks, ['language', 'codec'])
        expected_sorted_tracks = OrderedDict([
            (track_id, tracks[track_id]) for track_id in [0, 2, 3, 1]])

        assert isinstance(actual_sorted_tracks, OrderedDict)
        assert actual_sorted_tracks == expected_sorted_tracks
