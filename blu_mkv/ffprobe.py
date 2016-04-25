from abc import ABCMeta, abstractmethod
import json
import subprocess

from . import ProgramController


class AbstractFfprobeController(metaclass=ABCMeta):
    """Base class for Ffprobe controllers, providing abstract methods for
    Blu-ray disc analysis.
    """
    @abstractmethod
    def get_bluray_playlist_subtitles_with_frames_count(
            self, disc_path, playlist_id):
        pass


class FfprobeController(ProgramController, AbstractFfprobeController):
    """Interface with the Ffprobe program to analyze a Blu-ray disc.

    :param str executable_path: absolute path of the Ffprobe's executable file
    """
    def __init__(self, protocol='file', executable_file='ffprobe'):
        """
        :param str executable_file: name or absolute path of the Ffprobe's
                                    executable file
        """
        super().__init__(executable_file)
        self.protocol = protocol

    def count_subtitle_frames(self, file_path, **options):
        """Return streams' details of a specific Bluray disc's playlist like
        :meth:`~.get_all_streams_of_bluray_playlist_as_json`, but only for
        subtitle tracks.

        Subtitles' details contain the number of read frames for each subtitle
        track, which is especially useful to identify forced subtitles.
        This is only done for subtitles as this is a slow operation.

        :param str disc_path: Bluray disc's path
        :param int playlist_id: playlist's identifier
        :return: a list of dictionaries with subtitles' details
        :rtype: list
        """
        ffprobe_commandline = [
            self.executable_path,
            '-i', '{}:{}'.format(self.protocol, file_path),
            '-show_streams',
            '-select_streams', 's',
            '-count_frames',
            '-loglevel', 'quiet',
            '-print_format', 'json']

        for option, value in options:
            ffprobe_commandline.extend(['-{}'.format(option), value])

        ffprobe_output = subprocess.check_output(
            ffprobe_commandline,
            universal_newlines=True)

        return json.loads(ffprobe_output)
