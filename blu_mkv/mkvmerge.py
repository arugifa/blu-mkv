from abc import ABCMeta, abstractmethod
import json
import subprocess


class AbstractMkvmergeController(metaclass=ABCMeta):
    @abstractmethod
    def get_file_info(self, file_path):
        pass


class MkvmergeController(AbstractMkvmergeController):
    def get_file_info(self, file_path):
        """Return details about a media file.

        See Mkvmerge's documentation for more information about what kind of
        details are returned, when probing a file with the `--identify` option
        and outpout format set to JSON.

        :param str file_path: path of the file to probe
        :rtype: dict
        """
        mkvmerge_output = subprocess.check_output([
            'mkvmerge',
            '--identify',
            '--identification-format', 'json',
            file_path],
            universal_newlines=True)

        return json.loads(mkvmerge_output)
