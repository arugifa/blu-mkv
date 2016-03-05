from datetime import timedelta

import pytest

from blu_mkv import test
from blu_mkv.bluray import BlurayAnalyzer, BlurayDisc, BlurayPlaylist


@pytest.fixture(scope='session')
def ffprobe():
    return test.StubFfprobeController()


@pytest.fixture(scope='session')
def makemkv():
    return test.StubMakemkvController()


@pytest.fixture(scope='session')
def mkvmerge():
    return test.StubMkvmergeController()


@pytest.fixture(scope='session')
def bluray_analyzer(ffprobe, makemkv, mkvmerge):
    return BlurayAnalyzer(ffprobe, mkvmerge, makemkv)


@pytest.fixture(scope='session')
def bluray_disc(bluray_analyzer, bluray_dir):
    return BlurayDisc(str(bluray_dir), bluray_analyzer)


@pytest.fixture(scope='session')
def bluray_playlist(bluray_disc):
    return BlurayPlaylist(
        disc=bluray_disc,
        number=419,
        duration=timedelta(hours=2),
        size=33940936704)
