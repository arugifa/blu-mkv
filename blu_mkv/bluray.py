from datetime import timedelta
import re


class BlurayAnalyzer:
    """Analyze a Bluray disc by using Ffprobe and Mkvmerge command-line tools.

    :param str disc_path: path of the Bluray disc.
    :param ffprobe_controller: interface with Ffprobe.
    """
    def __init__(self, disc_path, ffprobe_controller):
        self.disc_path = disc_path
        self.ffprobe = ffprobe_controller

    def get_playlists(self):
        """Return playlists of the Bluray disc.

        Each playlist is a dictionary with the following details:
        - id: playlist's identifier as a string,
        - duration: playlist's duration, instance of
                    :class:`datetime.timedelta`.

        :return: list of found playlists.
        """
        playlists_details = re.findall(
            r'playlist (\d+).mpls \((\d+:\d{2}:\d{2})\)',
            self.ffprobe.get_unformatted_bluray_playlists(self.disc_path))

        playlists = list()
        for playlist in playlists_details:
            playlist_duration = [int(i) for i in playlist[1].split(':')]
            playlists.append({
                'id': playlist[0],
                'duration': timedelta(
                    hours=playlist_duration[0],
                    minutes=playlist_duration[1],
                    seconds=playlist_duration[2]),
            })
        return playlists
