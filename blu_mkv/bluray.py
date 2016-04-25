from pathlib import Path
import re

from cached_property import cached_property

from . import MultimediaFileAnalyzer, MultimediaFile
from .ffprobe import FfprobeController


COVERS_RELATIVE_PATH = "BDMV/META/DL"
PLAYLISTS_RELATIVE_PATH = "BDMV/PLAYLIST"


class BlurayAnalyzer(MultimediaFileAnalyzer):
    "Blu-ray disc analyzer using the Ffprobe, Mkvmerge and Makemkv programs."
    ffprobe_controller = FfprobeController('bluray')
    makemkv_controller = None

    def get_covers(self, disc_path):
        """Return covers present on a Bluray disc.

        Each cover is a dictionary with the following keys:
        - path: `str`, cover's absolute path,
        - size: `int`, cover's size in bytes.

        :param str disc_path: path of the Bluray disc. Must points to a
                              directory
        :return: list of found covers, sorted by path
        """
        covers_path = Path(disc_path, COVERS_RELATIVE_PATH)
        covers = [{
            'path': str(found_cover),
            'size': found_cover.stat().st_size,
        } for found_cover in covers_path.glob('*.jpg')]

        return sorted(covers, key=lambda cover: cover['path'])

    def get_playlists(self, disc_path):
        """Return details of playlists present on a Bluray disc by using
        Ffprobe.

        Details are dictionaries with the following keys:
        - duration: playlist duration, instance of :class:`datetime.timedelta`,
        - size: ``int``, playlist size in bytes.

        Playlists found without duration are skipped.

        :param str disc_path: path of the Bluray disc. Must points to a
                              directory
        :return: a dictionary of found playlists, with their number as key
        :return type: dict
        """
        all_playlist_paths = list(Path(disc_path).iterdir())

        playlists = dict()
        for playlist_path in all_playlist_paths:
            mkvmerge_analysis =\
                self.mkvmerge_controller.get_file_info(str(playlist_path))
            playlist_properties = mkvmerge_analysis['container']['properties']

            playlist_duration = playlist_properties.get('playlist_duration')
            if playlist_duration is None:
                # Playlists without duration are useless.
                continue

            playlist_number = int(playlist_path.stem)
            playlists.append(playlist_number)

        return playlists

    def _probe_with_mediainfo(self):
        result = super()._probe_with_mediainfo()

        all_tracks = result.xpath(
            './File/track[contains("Audio Text Video", @type)]')

        for track in all_tracks:
            track_id = track.find('ID')
            track_id.text = (
                re.match(r'\d+ \(.+\) / (\d+) \(.+\)', track_id.text)
                .group(1))

        return result


class BlurayDisc:
    """Bluray disc representation.

    Disc's items are accessed in a lazy fashion as such operations can be
    time-consuming (like probing playlists).

    :param path str: path of the disc
    :param bluray_analyzer: used to lazily probe the disc,
                            instance of :class:`.BlurayAnalyzer`
    """
    analyzer = BlurayAnalyzer()

    def __init__(self, path):
        self.path = path

    @cached_property
    def covers(self):
        """Return the disc's covers.

        See :meth:`.BlurayAnalyzer.get_covers` for more information about
        available covers' details.

        :rtype: list
        """
        return self.bluray_analyzer.get_covers(self.path)

    @cached_property
    def playlists(self):
        """Return the disc's playlists, sorted by number.

        Each playlist is an instance of :class:`.BlurayPlaylist`.
        Duplicate playlists are filtered in order to keep only one of them.

        :rtype: list
        """
        raw_playlists = self.bluray_analyzer.get_playlists(self.path)

        playlists = list()
        for (playlist_number, playlist_info) in sorted(raw_playlists.items()):
            playlist = BlurayPlaylist(self, playlist_number)

            if playlist not in playlists:
                playlists.append(playlist)

        return sorted(playlists, key=lambda playlist: playlist.number)

    def get_biggest_cover(self):
        """Return the biggest cover of the disc.

        The biggest cover is differentiated from other covers in terms of file
        size and not cover's dimensions.

        :return: the biggest cover if the disc have covers, `None` otherwise
        :rtype: dict or None
        """
        sorted_covers = sorted(
            self.covers, key=lambda cover: cover['size'], reverse=True)

        try:
            return sorted_covers[0]
        except IndexError:
            return None

    def get_movie_playlists(self, duration_factor=0.4):
        """Return the disc's movie playlists (e.g. director's cut, special
        edition, extended version, etc.).

        Movie playlists are usually longer than other playlists like bonuses.
        They are thus identified by applying a factor on the duration of the
        longest disc's playlist. All playlists which are longer than the result
        of this multiplication are considered as movie playlists.

        :param float duration_factor: used to identify movie playlists
        :rtype: list
        """
        if not self.playlists:
            return []

        longest_playlist = max(
            self.playlists, key=lambda playlist: playlist.duration)
        duration_limit = duration_factor * longest_playlist.duration

        return [playlist for playlist in self.playlists
                if playlist.duration >= duration_limit]


class BlurayPlaylist(MultimediaFile):
    "Bluray playlist representation."
    analyzer = BlurayAnalyzer()
