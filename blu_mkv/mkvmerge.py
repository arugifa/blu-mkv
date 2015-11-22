from abc import ABCMeta, abstractmethod
from pathlib import PurePath
import subprocess


class AbstractMkvmergeController(metaclass=ABCMeta):
    @abstractmethod
    def get_all_tracks_of_bluray_playlist(self, disc_path, playlist_id):
        pass


class MkvmergeController(AbstractMkvmergeController):
    def get_all_tracks_of_bluray_playlist(self, disc_path, playlist_id):
        playlist_path = PurePath(
            disc_path, 'BDMV/PLAYLIST/','{}.mpls'.format(playlist_id))
        return subprocess.check_output([
            'mkvmerge',
            '--identify-verbose',
            str(playlist_path)],
            universal_newlines=True)
