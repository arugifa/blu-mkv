import pytest

from blu_mkv.bluray import BlurayAnalyzer
from blu_mkv.ffprobe import FfprobeController
from blu_mkv.mkvmerge import MkvmergeController
from blu_mkv.test import StubFfprobeController, StubMkvmergeController


def pytest_addoption(parser):
    parser.addoption(
        '--bluray_path',
        action='append',
        default=[],
        help="Bluray disc's path to pass to Ffprobe and MkvMerge controllers")


def pytest_generate_tests(metafunc):
    if 'bluray_path' in metafunc.fixturenames:
        metafunc.parametrize(
            'bluray_path',
            metafunc.config.option.bluray_path,
            scope='session')


@pytest.fixture(
    scope='session',
    params=[FfprobeController, StubFfprobeController])
def ffprobe(request):
    return request.param()


@pytest.fixture(
    scope='session',
    params=[(FfprobeController, MkvmergeController),
            (StubFfprobeController, StubMkvmergeController)])
def bluray_analyzer(request, bluray_path):
    ffprobe_controller = request.param[0]()
    mkvmerge_controller = request.param[1]()
    return BlurayAnalyzer(bluray_path, ffprobe_controller, mkvmerge_controller)
