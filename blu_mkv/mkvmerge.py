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
            self, output_file_path, input_tracks, title=None,
            attachments=None):
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
            self, output_file_path, input_streams, title=None,
            attachments=None):
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

        :param str output_file_path: the Matroska file's path
        :param input_streams: list of dictionaries, streams to remux into the
                              Matroska file
        :param str title: title of the Matroska file (e.g., movie name)
        :param attachments: list of dictionaries, covert arts to embed in the
                            Matroska file
        :raises AssertionError: if ``input_streams`` is empty
        """
        assert input_streams, \
            "The 'input_streams' argument cannot be an empty list"

        # Command-line options for Mkvmerge must be ordered in a specific way.
        # Global options are defined at first.
        mkvmerge_commandline = [
            self.executable_path,
            '--output', output_file_path,
            '--title', title or '']

        if attachments:
            mkvmerge_commandline.extend(self._add_attachments(attachments))

        # Streams' options are grouped together, according to their source
        # file, and their original order is memorized. They will be added
        # further to the command-line.
        (grouped_streams, streams_order) =\
            self._group_input_streams_by_source_file(input_streams)

        # Streams' order belongs also to global options.
        mkvmerge_commandline.extend(self._set_streams_order(streams_order))

        # Options related to input streams are at last added to the
        # command-line.
        for (source_file_id, (source_file_path, streams)) in enumerate(grouped_streams.items()):  # noqa
            mkvmerge_commandline.extend(
                self._add_streams(source_file_id, source_file_path, streams))

        # And the complete command-line is executed.
        subprocess.check_call(mkvmerge_commandline)

    @staticmethod
    def _group_input_streams_by_source_file(input_streams):
        """Group input streams by source file, while memorizing their original
        order."""
        streams_order = []
        grouped_streams = OrderedDict()

        for stream in input_streams:
            source_files = list(grouped_streams.keys())
            source_file_path = stream['file_path']
            try:
                source_file_id = source_files.index(source_file_path)
            except ValueError:
                source_file_id = len(source_files)
                grouped_streams[source_file_path] = list()

            streams_order.append((source_file_id, stream['id']))
            grouped_streams[source_file_path].append(stream)

        return (grouped_streams, streams_order)

    @staticmethod
    def _add_attachments(attachments):
        """Return command-line options to add attachments to a Matroska
        file."""
        mkvmerge_options = list()

        for attachment in attachments:
            mkvmerge_options.extend([
                '--attachment-mime-type', attachment['type'],
                '--attachment-name', attachment['name'],
                '--attach-file', attachment['path']])

        return mkvmerge_options

    @staticmethod
    def _set_streams_order(streams_order):
        """Return command-line option to set streams order in a Matroska
        file."""
        return [
            '--track-order',
            ','.join(
                '{}:{}'.format(source_file_id, stream_id)
                for (source_file_id, stream_id) in streams_order)]

    @staticmethod
    def _add_streams(source_file_id, source_file_path, input_streams):
        """Return command-line options to add input streams to a Matroska
        file."""
        mkvmerge_options = list()

        stream_types = {
            'audio': list(),
            'subtitle': list(),
            'video': list()}

        for stream in input_streams:
            default_flag = 1 if stream['properties'].get('default') else 0
            forced_flag = 1 if stream['properties'].get('forced') else 0
            track_name = stream['properties'].get('name', '')

            mkvmerge_options.extend([
                '--default-track', '{}:{}'.format(stream['id'], default_flag),
                '--forced-track', '{}:{}'.format(stream['id'], forced_flag),
                '--track-name', '{}:{}'.format(stream['id'], track_name)])

            stream_types[stream['type']].append(str(stream['id']))

        mkvmerge_options.extend([
            '--audio-tracks', ','.join(stream_types['audio']),
            '--subtitle-tracks', ','.join(stream_types['subtitle']),
            '--video-tracks', ','.join(stream_types['video']),
            source_file_path])

        return mkvmerge_options
