from abc import ABCMeta, abstractmethod
from pathlib import PurePath
import re
import subprocess

from .bluray import PLAYLISTS_RELATIVE_PATH


class AbstractMkvmergeController(metaclass=ABCMeta):
    @abstractmethod
    def get_bluray_playlist_tracks(self, disc_path, playlist_id):
        pass


class MkvmergeController(AbstractMkvmergeController):
    def get_bluray_playlist_tracks(self, disc_path, playlist_number):
        """Return tracks' details of a specific Bluray disc's playlist.

        Details are dictionaries with the following keys:
        - type: `str`, track's type (e.g. video, audio, subtitle),
        - codec: `str`, track's codec (e.g. H.264, DTS, PGS),
        - properties: `dict`, track's properties (e.g. video's dimensions,
                      audio channels, language). Available properties depend
                      on the track's codec.

        :param str disc_path: Bluray disc's path
        :param int playlist_number: playlist's number
        :return: a dictionary of found tracks, with their identifier as key
        :rtype: dict
        """
        playlist_path = PurePath(
            disc_path,
            PLAYLISTS_RELATIVE_PATH,
            '{:05d}.mpls'.format(playlist_number))

        mkvmerge_output = subprocess.check_output([
            'mkvmerge',
            '--identify-verbose',
            str(playlist_path)],
            universal_newlines=True)

        # In Mkvmerge's output, find lines like:
        # "Track ID 0: video (MPEG-4p10/AVC/h.264) [pixel_dimensions:1920x1080 ts_pid:4113]"  # noqa
        raw_tracks = re.findall(
            r'Track ID (\d+): (\w+) \((.+)\) \[(.+)\]', mkvmerge_output)

        tracks = dict()
        for track in raw_tracks:
            track_id = int(track[0])

            track_properties = dict()
            for track_property in track[3].split(' '):
                (property_name, property_value) = track_property.split(':')
                track_properties[property_name] = property_value

            tracks[track_id] = {
                'type': track[1],
                'codec': track[2],
                'properties': track_properties}

        return tracks
