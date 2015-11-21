from abc import ABCMeta, abstractmethod
import json
import re
import subprocess


class AbstractFfprobeController(metaclass=ABCMeta):
    @abstractmethod
    def get_unformatted_bluray_playlists(self, disc_path):
        pass

    @abstractmethod
    def get_all_streams_of_bluray_playlist_as_json(
            self, disc_path, playlid_id=None):
        pass


class FfprobeController(AbstractFfprobeController):
    def get_unformatted_bluray_playlists(self, disc_path):
        """Analyze Bluray disc in search of its playlists, and returns
        the unformatted Ffprobe's output.

        In the output, lines relative to playlists look like:
        "[bluray @ 0x5596c189ee60] playlist 00419.mpls (2:23:11)"

        :param str disc_path: Bluray disc's path
        :return: Unformatted Ffprobe's output containing playlists' details
        :rtype: str
        """
        return self._analyze_bluray_disc(disc_path)

    def get_all_streams_of_bluray_playlist_as_json(
            self, disc_path, playlist_id=None):
        ffprobe_options = ['-show_streams']
        if playlist_id is not None:
            ffprobe_options.extend(['-playlist', playlist_id])

        return self._analyze_bluray_disc(
            disc_path, ffprobe_options, json_output=True)

    @staticmethod
    def _clean_formatted_output(ffprobe_output):
        """Delete insignificant error messages appearing in ffprobe's output.

        These errors can make unusable outputs using special formats like JSON
        or CSV. Only one error (about missing JVM libary for BD-J) is handled
        for the moment.
        """
        return re.sub(r'bdj.c:\d+: BD-J check: Failed to load JVM library\n',
                      r'', ffprobe_output, count=1)

    def _analyze_bluray_disc(
            self, disc_path, ffprobe_options=None, json_output=False):
        """Analyze a Bluray disc by using Ffprobe command-line tool.

        The command-line can be customized by filling additional Ffprobe's
        options.

        :param str disc_path: Bluray disc's path
        :param list ffprobe_options: Ffprobe's options.
        :param bool json_output: define format of Ffprobe's output.
        :return: result of the analysis.
        :return type: an unformatted string if json_output is false;
                      a dictionary otherwise.
        """
        ffprobe_commandline = [
            'ffprobe',
            '-i', 'bluray:{}'.format(disc_path)]
        ffprobe_commandline.extend(ffprobe_options or [])

        if json_output is False:
            return subprocess.check_output(
                ffprobe_commandline,
                stderr=subprocess.STDOUT,
                universal_newlines=True)
        else:
            ffprobe_commandline.extend([
                '-loglevel', 'quiet',
                '-print_format', 'json'])
            ffprobe_output = subprocess.check_output(
                ffprobe_commandline,
                universal_newlines=True)
            return json.loads(self._clean_formatted_output(ffprobe_output))
