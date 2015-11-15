import pytest

from blu_mkv.bluray import BlurayAnalyzer
from blu_mkv.test import FfprobeStubController


@pytest.fixture(scope='session')
def bluray_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('bluray_disc')


@pytest.fixture(scope='session')
def ffprobe():
    return FfprobeStubController()


@pytest.fixture(scope='session')
def bluray_analyzer(bluray_dir, ffprobe):
    return BlurayAnalyzer(str(bluray_dir), ffprobe)
