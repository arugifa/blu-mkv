import pytest

from blu_mkv.bluray import BlurayAnalyzer
from blu_mkv.ffprobe import FfprobeController
from blu_mkv.test import StubFfprobeController


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
    scope='session', params=[FfprobeController, StubFfprobeController])
def ffprobe(request):
    return request.param()


@pytest.fixture(scope='session')
def bluray_analyzer(bluray_path, ffprobe):
    return BlurayAnalyzer(bluray_path, ffprobe)
