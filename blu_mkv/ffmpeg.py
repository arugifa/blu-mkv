import subprocess


class FfprobeController:
    """Interface with Ffprobe command-line interface."""

    @staticmethod
    def get_unformatted_bluray_playlists(disc_path):
        """Analyze Bluray disc in search of its playlists, and returns
        the unformatted Ffprobe's output.

        In the output, lines relative to playlists look like:
        "[bluray @ 0x5596c189ee60] playlist 00419.mpls (2:23:11)"

        :param str disc_path: Bluray disc's path
        :return: Unformatted Ffprobe's output containing playlists' details
        :rtype: str
        """
        return subprocess.check_output([
            'ffprobe',
            '-i', 'bluray:{}'.format(disc_path)],
            stderr=subprocess.STDOUT,
            universal_newlines=True)
