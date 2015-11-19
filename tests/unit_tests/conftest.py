import pytest

from blu_mkv.bluray import BlurayAnalyzer
from blu_mkv.test import FfprobeStubController


@pytest.fixture(scope='session')
def bluray_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('bluray_disc')


@pytest.fixture(scope='session')
def bluray_covers(bluray_dir):
    covers_dir = bluray_dir \
                 .mkdir('BDMV') \
                 .mkdir('META') \
                 .mkdir('DL')

    small_cover = covers_dir.join('small_cover.jpg')
    small_cover.write_binary(b"fake cover")

    big_cover = covers_dir.join('big_cover.jpg')
    big_cover.write_binary(b"fake BIG cover")

    return [big_cover, small_cover]


@pytest.fixture(scope='session')
def ffprobe():
    return FfprobeStubController()


@pytest.fixture(scope='session')
def bluray_analyzer(bluray_dir, ffprobe):
    return BlurayAnalyzer(str(bluray_dir), ffprobe)
