from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import json
import subprocess

from . import ProgramController


class AbstractMkvmergeController(metaclass=ABCMeta):
    @abstractmethod
    def get_file_info(self, file_path):
        pass

    @abstractmethod
    def write(
            self, output_file, input_tracks, title=None, attachments=None):
        pass


class MkvmergeController(ProgramController, AbstractMkvmergeController):
    """Interface with the Mkvmerge program.

    :param str executable_path: absolute path of the Mkvmerge's executable file
    """
    def __init__(self, executable_file='mkvmerge'):
        """
        :param str executable_file: name or absolute path of the Mkvmerge's
                                    executable file
        """
        super().__init__(executable_file)

    def get_file_info(self, file_path):
        """Return details about a media file.

        See Mkvmerge's documentation for more information about what kind of
        details are returned, when probing a file with the `--identify` option
        and outpout format set to JSON.

        :param str file_path: path of the file to probe
        :rtype: dict
        """
        mkvmerge_output = subprocess.check_output([
            self.executable_path,
            '--identify',
            '--identification-format', 'json',
            file_path],
            universal_newlines=True)

        return json.loads(mkvmerge_output)

    def write(
            self, output_file, input_files, tracks_order, title=None,
            external_attachments=None):
        """Remux several streams into a Matroska file.

        Each stream is a dictionary with following information:
        - file_path: `str`, path of the file to which belongs the stream
        - id: `int`, stream's identifier inside its source file
        - type: `str`, stream's type. Can be either 'audio', 'subtitle' or
                'video'
        - properties: dictionary of properties to set on the stream inside the
                      Matroska file

        Streams' properties can have the following details (none of them are
        mandatory):
        - default: `bool`, set or unset the default flag
        - forced: `bool`, set or unset the forced flag
        - name: `str`, name of the stream

        Additionally, attachments (i.e., cover arts) can be embedded inside the
        Matroska file. They must have the following details:
        - type: `str`, mime-type of the attachment, as defined by the IANA
        - name: `str`, name used for the attachment inside the Matroska file
                (e.g., cover.jpg). See the Matroska documentation for knowing
                how to name attachments according to their size
        - path: `str`, path of the original attachment

        :param str output_file: the Matroska file's path
        :param input_streams: list of dictionaries, streams to remux into the
                              Matroska file
        :param str title: title of the Matroska file (e.g., movie name)
        :param attachments: list of dictionaries, covert arts to embed in the
                            Matroska file
        :raises AssertionError: if ``input_streams`` is empty
        """
        assert input_files, \
            "The 'input_files' argument cannot be an empty list"

        input_files = OrderedDict(
            sorted(input_files.items(), key=lambda input_file: input_file[0]))

        # Command-line options for Mkvmerge must be ordered in a specific way.
        # Global options are defined at first.
        mkvmerge_commandline = [
            self.executable_path,
            '--output', output_file,
            '--title', title or '']

        if external_attachments:
            mkvmerge_commandline.extend(
                self._add_external_attachments(external_attachments))

        self._set_tracks_order(tracks_order, input_files)

        for (count, file_path) in enumerate(input_files):
            file_options = self._set_input_file_options(
                count, file_path, input_files[file_path])
            mkvmerge_commandline.extend(file_options)

        # And the complete command-line is executed.
        subprocess.check_call(mkvmerge_commandline)

    @staticmethod
    def _add_external_attachments(attachments):
        "Return command-line options to add external attachments."
        mkvmerge_options = list()

        for attachment in attachments:
            mkvmerge_options.extend([
                '--attachment-mime-type', attachment['type'],
                '--attachment-name', attachment['name'],
                '--attach-file', attachment['path']])

        return mkvmerge_options

    @staticmethod
    def _set_tracks_order(tracks_order, input_files):
        "Return command-line option to set streams order."
        input_file_paths = list(input_files)

        return [
            '--track-order',
            ','.join(
                '{}:{}'.format(input_file_paths.index(input_file), track_id)
                for (input_file, track_id) in tracks_order)]

    @staticmethod
    def _set_input_file_options(file_id, file_path, file_items):
        "Return command-line options specific to an input file."
        mkvmerge_options = list()

        tracks_options = {
            'audio': list(),
            'subtitles': list(),
            'video': list()}

        for track in file_items['tracks']:
            default_flag = 1 if track['properties'].get('default') else 0
            forced_flag = 1 if track['properties'].get('forced') else 0
            track_name = track['properties'].get('name', '')

            mkvmerge_options.extend([
                '--default-track', '{}:{}'.format(track['id'], default_flag),
                '--forced-track', '{}:{}'.format(track['id'], forced_flag),
                '--track-name', '{}:{}'.format(track['id'], track_name)])

            tracks_options[track['type']].append(str(track['id']))

        mkvmerge_options.extend([
            '--audio-tracks', ','.join(tracks_options['audio']),
            '--subtitle-tracks', ','.join(tracks_options['subtitles']),
            '--video-tracks', ','.join(tracks_options['video']),
            '--attachments', ','.join(map(str, file_items['attachments'])),
            file_path])

        return mkvmerge_options
