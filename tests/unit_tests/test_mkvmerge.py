import subprocess

import pytest

from blu_mkv.mkvmerge import MkvmergeController


@pytest.fixture(scope='function')
def mock_mkvmerge(mock):
    mock.patch.object(subprocess, 'check_call')
    return MkvmergeController()


class TestMkvmergeController:
    def test_write_with_no_input_streams(self, mock_mkvmerge):
        with pytest.raises(AssertionError):
            mock_mkvmerge.write('/movie.mkv', [])

    def test_write_with_only_required_options_set(self, mock_mkvmerge):
        input_streams = [{
            'file_path': "/tmp/bluray",
            'id': 0,
            'type': "video",
            'properties': dict()}]

        mock_mkvmerge.write('/movie.mkv', input_streams)

        subprocess.check_call.assert_called_once_with([
            'mkvmerge',
            '--output', '/movie.mkv',
            '--title', '',
            '--track-order', '0:0',
            '--default-track', '0:0',
            '--forced-track', '0:0',
            '--track-name', '0:',
            '--audio-tracks', '',
            '--subtitle-tracks', '',
            '--video-tracks', '0',
            '/tmp/bluray'])

    def test_write_with_all_options_set(self, mock_mkvmerge):
        input_streams = [
            {
                'file_path': "/tmp/bluray_1",
                'id': 0,
                'type': "video",
                'properties': {'default': True}
            },
            {
                'file_path': "/tmp/bluray_1",
                'id': 1,
                'type': "video",
                'properties': {'default': False}
            },
            {
                'file_path': "/tmp/bluray_2",
                'id': 1,
                'type': "audio",
                'properties': dict(),
            },
            {
                'file_path': "/tmp/bluray_2",
                'id': 2,
                'type': "audio",
                'properties': {'name': "Director's commentary"},
            },
            {
                'file_path': "/tmp/bluray_2",
                'id': 3,
                'type': "subtitle",
                'properties': {'forced': False},
            },
            {
                'file_path': "/tmp/bluray_1",
                'id': 4,
                'type': "subtitle",
                'properties': {'forced': True},
            },
            {
                'file_path': "/tmp/bluray_1",
                'id': 3,
                'type': "subtitle",
                'properties': dict(),
            },
        ]

        attachments = [
            {
                'type': "jpeg",
                'name': "cover.jpg",
                'path': "/tmp/bluray_cover.jpg",
            },
            {
                'type': "jpeg",
                'name': "small_cover.jpg",
                'path': "/tmp/bluray_small_cover.jpg",
            },
        ]

        mock_mkvmerge.write(
            '/movie.mkv', input_streams, title='Super Movie',
            attachments=attachments)

        subprocess.check_call.assert_called_once_with([
            'mkvmerge',

            # Global options
            '--output', '/movie.mkv',
            '--title', 'Super Movie',

            '--attachment-mime-type', 'jpeg',
            '--attachment-name', 'cover.jpg',
            '--attach-file', '/tmp/bluray_cover.jpg',

            '--attachment-mime-type', 'jpeg',
            '--attachment-name', 'small_cover.jpg',
            '--attach-file', '/tmp/bluray_small_cover.jpg',

            '--track-order', '0:0,0:1,1:1,1:2,1:3,0:4,0:3',

            # First disc's options
            #  First disc's video tracks
            '--default-track', '0:1',
            '--forced-track', '0:0',
            '--track-name', '0:',

            '--default-track', '1:0',
            '--forced-track', '1:0',
            '--track-name', '1:',

            #  First disc's subtitle tracks
            '--default-track', '4:0',
            '--forced-track', '4:1',
            '--track-name', '4:',

            '--default-track', '3:0',
            '--forced-track', '3:0',
            '--track-name', '3:',

            #  First disc's selected tracks
            '--audio-tracks', '',
            '--subtitle-tracks', '4,3',
            '--video-tracks', '0,1',

            #  First disc's path
            '/tmp/bluray_1',

            # Second disc's options
            #  Second disc's audio tracks
            '--default-track', '1:0',
            '--forced-track', '1:0',
            '--track-name', '1:',

            '--default-track', '2:0',
            '--forced-track', '2:0',
            '--track-name', "2:Director's commentary",

            #  Second disc's subtitle tracks
            '--default-track', '3:0',
            '--forced-track', '3:0',
            '--track-name', '3:',

            #  Second disc's selected tracks
            '--audio-tracks', '1,2',
            '--subtitle-tracks', '3',
            '--video-tracks', '',

            #  Second disc's path
            '/tmp/bluray_2'])
