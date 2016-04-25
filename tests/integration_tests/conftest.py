import argparse
from pathlib import Path

import pytest

from blu_mkv.bluray import BlurayAnalyzer
from blu_mkv.ffprobe import FfprobeController
from blu_mkv.makemkv import MakemkvController
from blu_mkv.mkv import MkvAnalyzer
from blu_mkv.mkvmerge import MkvmergeController


class StoreBlurayPath(argparse._StoreAction):
    def __call__(self, parser, namespace, values, option_string=None):
        assert Path(values[0]).is_dir(), \
            "{} must points to a directory".format(option_string)
        return super().__call__(parser, namespace, values, option_string)


class StoreMkvPath(argparse._StoreAction):
    def __call__(self, parser, namespace, values, option_string=None):
        assert Path(values[0]).is_file(), \
            "{} must points to a file".format(option_string)
        return super().__call__(parser, namespace, values, option_string)


def pytest_addoption(parser):
    parser.addoption(
        '--bluray_path',
        action=StoreBlurayPath,
        default=[],
        nargs=1,
        help="Path of the Blu-ray disc to analyze")

    parser.addoption(
        '--mkv_path',
        action=StoreMkvPath,
        default=[],
        nargs=1,
        help="Path of the Matroska file to analyze")


def pytest_generate_tests(metafunc):
    if 'bluray_path' in metafunc.fixturenames:
        metafunc.parametrize(
            'bluray_path',
            metafunc.config.option.bluray_path,
            scope='session')

    if 'mkv_path' in metafunc.fixturenames:
        metafunc.parametrize(
            'mkv_path',
            metafunc.config.option.mkv_path,
            scope='session')


@pytest.fixture(scope='session')
def ffprobe():
    return FfprobeController()


@pytest.fixture(scope='session')
def makemkv():
    return MakemkvController()


@pytest.fixture(scope='session')
def mkvmerge():
    return MkvmergeController()


@pytest.fixture(scope='session')
def bluray_analyzer(request, ffprobe, makemkv, mkvmerge):
    return BlurayAnalyzer(ffprobe, mkvmerge, makemkv)


@pytest.fixture(scope='session')
def mkv_analyzer(request, ffprobe, mkvmerge):
    return MkvAnalyzer(ffprobe, mkvmerge)
