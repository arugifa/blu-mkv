import pytest

from blu_mkv.bluray import BlurayAnalyzer

from blu_mkv.test import StubFfprobeController


@pytest.fixture(scope='session')
def ffprobe():
    return StubFfprobeController()


@pytest.fixture(scope='session')
def bluray_analyzer(bluray_dir, ffprobe):
    return BlurayAnalyzer(str(bluray_dir), ffprobe)
