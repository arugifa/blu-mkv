from collections import OrderedDict


def filter_tracks(tracks, **filters):
    """Return a subset of tracks by applying filters.

    :param dict tracks: original tracks. Prefer the use of an ordered
                        dictionary to keep order on filtered tracks
    :param **filters: filters to apply on original tracks,
                      with tracks' property names as argument names,
                      and ``list`` of possible values as argument values
    :return: the filtered tracks
    :rtype: instance of :class:`~collections.OrderedDict`
    """
    if not filters:
        return tracks

    selected_tracks = OrderedDict()
    for (track_id, track_info) in tracks.items():
        for (field, possible_values) in filters.items():
            if (field not in track_info or
                    track_info[field] not in possible_values):
                break
        else:
            selected_tracks[track_id] = track_info

    return selected_tracks


def sort_tracks(tracks, properties=None):
    """Return tracks sorted by their property values and identifier.

    :param dict tracks: the tracks to sort
    :param list properties: tracks' property names used for the sorting
    :return: the sorted tracks
    :rtype: instance of :class:`~collections.OrderedDict`
    """
    properties = properties or []

    def compare_tracks(track):
        track_id = track[0]
        track_info = track[1]

        compared_properties = [
            track_info.get(property) for property in properties]
        return (compared_properties, track_id)

    return OrderedDict(sorted(tracks.items(), key=compare_tracks))
