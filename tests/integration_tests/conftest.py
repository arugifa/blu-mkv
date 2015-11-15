import pytest

from blu_mkv.ffmpeg import FfprobeController
from blu_mkv.test import FfprobeStubController


def pytest_addoption(parser):
    parser.addoption(
        '--bluray_path',
        action='append',
        default=[],
        help="Bluray disc's path to pass to Ffprobe and MkvMerge controllers")


def pytest_generate_tests(metafunc):
    if 'bluray_path' in metafunc.fixturenames:
        metafunc.parametrize('bluray_path', metafunc.config.option.bluray_path)


@pytest.fixture(
    scope='module', params=[FfprobeController, FfprobeStubController])
def ffprobe(request):
    return request.param()
