import pytest

from blu_mkv.bluray import BlurayAnalyzer

from blu_mkv.test import StubFfprobeController, StubMkvmergeController


@pytest.fixture(scope='session')
def ffprobe():
    return StubFfprobeController()


@pytest.fixture(scope='session')
def mkvmerge():
    return StubMkvmergeController()


@pytest.fixture(scope='session')
def bluray_analyzer(ffprobe, mkvmerge):
    return BlurayAnalyzer(ffprobe, mkvmerge)
