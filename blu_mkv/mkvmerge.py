from abc import ABCMeta, abstractmethod
from pathlib import PurePath
import subprocess


class AbstractMkvmergeController(metaclass=ABCMeta):
    @abstractmethod
    def get_all_tracks_of_bluray_playlist(self, disc_path, playlist_id):
        pass


class MkvmergeController(AbstractMkvmergeController):
    def get_all_tracks_of_bluray_playlist(self, disc_path, playlist_id):
        """Analyze Bluray disc in search of its tracks, and returns
        the unformatted Mkvmerge's output.

        In the output, lines relative to tracks look like:
        "Track ID 3: subtitles (HDMV PGS) [language:fre ts_pid:4608]"

        :param str disc_path: Bluray disc's path
        :return: Unformatted Mkvmerge's output containing tracks' details
        :rtype: str
        """
        playlist_path = PurePath(
            disc_path, 'BDMV/PLAYLIST/','{}.mpls'.format(playlist_id))
        return subprocess.check_output([
            'mkvmerge',
            '--identify-verbose',
            str(playlist_path)],
            universal_newlines=True)
