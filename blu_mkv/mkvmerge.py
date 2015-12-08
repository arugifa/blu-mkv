from abc import ABCMeta, abstractmethod
import json
from pathlib import PurePath
import subprocess

from .bluray import PLAYLISTS_RELATIVE_PATH


class AbstractMkvmergeController(metaclass=ABCMeta):
    @abstractmethod
    def get_bluray_playlist_info(self, disc_path, playlist_id):
        pass


class MkvmergeController(AbstractMkvmergeController):
    def get_bluray_playlist_info(self, disc_path, playlist_number):
        """Return details about a specific Bluray disc's playlist.

        See Mkvmerge's documentation for more information about what kind of
        details are returned, when probing a playlist with the `--identify`
        option and outpout format set to JSON.

        :param str disc_path: Bluray disc's path
        :param int playlist_number: playlist's number
        :rtype: dict
        """
        playlist_path = PurePath(
            disc_path,
            PLAYLISTS_RELATIVE_PATH,
            '{:05d}.mpls'.format(playlist_number))

        mkvmerge_output = subprocess.check_output([
            'mkvmerge',
            '--identify',
            '--identification-format', 'json',
            str(playlist_path)],
            universal_newlines=True)

        return json.loads(mkvmerge_output)
