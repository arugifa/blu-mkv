from abc import ABCMeta, abstractmethod
from enum import Enum
import re
import subprocess

from . import ProgramController
from .exceptions import ControllerError


class ItemAttribute(Enum):
    """Information returned by Makemkv during analysis of a Blu-ray disc, for
    each title or stream found.

    Based on makemkv-oss/makemkvgui/inc/lgpl/apdefs.h
    """
    type = 1
    name = 2
    lang_code = 3
    lang_name = 4
    codec_id = 5
    codec_short = 6
    codec_long = 7
    chapter_count = 8
    duration = 9
    disk_size = 10
    disk_size_bytes = 11
    stream_type_extension = 12
    bitrate = 13
    audio_channels_count = 14
    angle_info = 15
    source_file_name = 16
    audio_sample_rate = 17
    audio_sample_size = 18
    video_size = 19
    video_aspect_ratio = 20
    video_frame_rate = 21
    stream_flags = 22
    date_time = 23
    original_title_id = 24
    segments_count = 25
    segments_map = 26
    output_file_name = 27
    metadata_language_code = 28
    metadata_language_name = 29
    tree_info = 30
    panel_title = 31
    volume_name = 32
    order_weight = 33
    output_format = 34
    output_format_description = 35
    seamless_info = 36
    panel_text = 37
    mkv_flags = 38
    mkv_flags_text = 39
    audio_channel_layout_name = 40
    output_codec_short = 41
    output_conversion_type = 42
    output_audioSample_rate = 43
    output_audio_sample_size = 44
    output_audio_channels_count = 45
    output_audio_channel_layout_name = 46
    output_audio_channel_layout = 47
    output_audio_mix_description = 48


class AbstractMakemkvController(metaclass=ABCMeta):
    @abstractmethod
    def get_disc_info(self, source_type, source_name):
        pass


class MakemkvController(ProgramController, AbstractMakemkvController):
    """Interface with the Makemkv program.

    :param str executable_path: absolute path of the Makemkv command-line's
                                executable file
    """
    def __init__(self, executable_file='makemkvcon'):
        """
        :param str executable_file: name or absolute path of the Makemkv
                                    command-line's executable
        """
        super().__init__(executable_file)

    def get_disc_info(self, source_type, source_name):
        """Return details about a Blu-ray disc.

        Details are organized in a dictionary as follows:
        - a top-level key ``titles`` collects all titles, with their index
          number as key,
        - for each title, a key ``streams`` collects all streams, with their
          index number as key.

        See :class:`.AttributeItem` for more information about what kind of
        details can be returned for each title or playlist.

        :param str source_type: type of the disc to probe. See makemkvcon's
                                documentation for available types
        :param str source_name: path or identifier of the disc
        :rtype: dict
        """
        try:
            makemkv_output = subprocess.check_output([
                self.executable_path,
                '-r', 'info',
                '{}:{}'.format(source_type, source_name)],
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            raise ControllerError(exc.stdout.splitlines()[-1]) from exc

        # Regex for lines related to titles. Example: TINFO:0,8,0,"22"
        title_regex = re.compile(
            r'TINFO:'
            r'(?P<title_id>\d+),(?P<attribute_id>\d+),\d+,'
            r'"(?P<attribute_value>.+)"')

        # Regex for lines related to streams. Example: SINFO:0,0,22,0,"8192"
        stream_regex = re.compile(
            r'SINFO:'
            r'(?P<title_id>\d+),(?P<stream_id>\d+),(?P<attribute_id>\d+),\d+,'
            r'"(?P<attribute_value>.+)"')

        disc_info = {'titles': dict()}
        for line in makemkv_output.splitlines():
            # Start by searching lines related to streams,
            # as they are more of them.
            stream_match = stream_regex.match(line)
            if stream_match:
                self._fill_stream_properties(stream_match, disc_info)
                continue

            title_match = title_regex.match(line)
            if title_match:
                self._fill_title_properties(title_match, disc_info)

        return disc_info

    def _fill_title_properties(self, regex_match, disc_info):
        """Fill details for each title found."""
        title_id = int(regex_match.group('title_id'))
        attribute_name =\
            ItemAttribute(int(regex_match.group('attribute_id'))).name
        attribute_value = regex_match.group('attribute_value')

        disc_titles = disc_info['titles']
        try:
            disc_titles[title_id][attribute_name] = attribute_value
        except KeyError:
            disc_titles[title_id] = {
                'streams': dict(),
                attribute_name: attribute_value}

    def _fill_stream_properties(self, regex_match, disc_info):
        """Fill details for each playlist found."""
        title_id = int(regex_match.group('title_id'))
        stream_id = int(regex_match.group('stream_id'))
        attribute_name =\
            ItemAttribute(int(regex_match.group('attribute_id'))).name
        attribute_value = regex_match.group('attribute_value')

        title_streams = disc_info['titles'][title_id]['streams']
        try:
            title_streams[stream_id][attribute_name] = attribute_value
        except KeyError:
            title_streams[stream_id] = {attribute_name: attribute_value}
