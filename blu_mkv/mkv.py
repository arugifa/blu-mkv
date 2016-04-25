from collections import OrderedDict

from cached_property import cached_property


class MkvAnalyzer:
    def __init__(self, mkvmerge_controller):
        self.mkvmerge_controller = mkvmerge_controller

    def get_properties(self, file_path):
        mkvmerge_analysis = self.mkvmerge_controller.get_file_info(file_path)
        properties = mkvmerge_analysis['container']['properties']

        attachments = self._get_attachments(mkvmerge_analysis)
        tracks = self._get_tracks(mkvmerge_analysis)

        return {
            'attachments': attachments,
            'title': properties.get('title'),
            'tracks': tracks}

    def _get_attachments(self, mkvmerge_analysis):
        all_attachments = dict()

        for attachment in mkvmerge_analysis['attachments']:
            attachment_id = attachment['id']
            all_attachments[attachment_id] = {
                'name': attachment['file_name'],
                'size': attachment['size']}

        return all_attachments

    def _get_tracks(self, mkvmerge_analysis):
        all_tracks = {
            track_type: dict()
            for track_type in ['audio', 'subtitles', 'video']}

        for track in mkvmerge_analysis['tracks']:
            track_id = track['id']
            track_type = track['type']

            all_tracks[track_type][track_id] = {
                'language_code': track['properties'].get('language'),
                'uid': track['properties']['number']}

        return all_tracks


class MkvFile:
    def __init__(self, path, mkv_analyzer):
        self.path = path
        self.mkv_analyzer = mkv_analyzer

    @cached_property
    def _properties(self):
        properties = self.disc.mkv_analyzer.get_properties(self.path)

        tracks = properties['tracks']
        for (track_type, tracks) in tracks.items():
            tracks[track_type] = self._sort_tracks(tracks)

        return properties

    @staticmethod
    def _sort_tracks(tracks):
        """Sort tracks by ID."""
        return OrderedDict(sorted(tracks.items(), key=lambda track: track[0]))
