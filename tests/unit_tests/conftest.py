from datetime import timedelta

import pytest

from blu_mkv.bluray import BlurayAnalyzer, BlurayDisc, BlurayPlaylist
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


@pytest.fixture(scope='session')
def bluray_disc(bluray_analyzer, bluray_dir):
    return BlurayDisc(str(bluray_dir), bluray_analyzer)


@pytest.fixture(scope='session')
def bluray_playlist(bluray_disc):
    return BlurayPlaylist(
        disc=bluray_disc,
        number=419,
        duration=timedelta(hours=2),
        size=33940936704,
        bit_rate=31605890)
