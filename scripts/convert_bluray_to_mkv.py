#!/usr/bin/env python

"""Provide a script to convert a Blu-ray disc to Matroska file."""

import argparse
from pathlib import Path
import subprocess
import sys


def main(args):
    bluray_path = Path(args.src_disc)
    destination_directory = Path(args.dst_dir)

    # Mount the Blu-ray disc if it is a disk image.
    if bluray_path.is_file():
        mount_point = Path('/tmp', bluray_path.stem)

        try:
            mount_point.mkdir()
            utils.mount_disk_image(str(bluray_path), str(mount_point))
        except (OSError, subprocess.CalledProcessError) as exc:
            mount_point.rmdir()
            sys.exit("Unable to mount disk image: {}".format(exc))
        else:
            bluray_path = mount_point
    else:
        mount_point = None

    try:
        # Initialize Ffprobe, Makemkv and Mkvmerge controllers
        # to analyze the disc.
        all_controllers = list()
        for (controller_name, controller_class) in [
                ('Ffprobe', FfprobeController),
                ('Mkvmerge', MkvmergeController),
                ('Makemkv', MakemkvController)]:
            try:
                all_controllers.append(controller_class())
            except FileNotFoundError as exc:
                sys.exit(
                    "Unable to locate {}'s executable: {}"
                    .format(controller_name, exc))

        bluray_analyzer = bluray.BlurayAnalyzer(*all_controllers)
        bluray_disc = bluray.BlurayDisc(bluray_path, bluray_analyzer)

        # Convert all movie playlists (not bonuses) found on the disc.
        movie_playlists = bluray_disc.get_movie_playlists()
        movie_playlists_count = len(movie_playlists)
        print("Found {} movie playlist(s)".format(movie_playlists_count))
        if (args.playlists_count and
                movie_playlists_count > args.playlists_count):
            sys.exit(
                "Only {} playlist(s) can be converted. "
                "Consider increasing the value for the '--playlists_count' "
                "option".format(args.playlists_count))

        for playlist in bluray_disc.get_movie_playlists():
            print("Start analysis of playlist {}".format(playlist.number))

            if playlist.has_multiview():
                print(
                    "Skip playlist {}: "
                    "conversion of 3D playlists is currently not supported"
                    .format(playlist.number))
                continue

            # Only the biggest disc cover is kept.
            cover_art = bluray_disc.get_biggest_cover()
            if cover_art is not None:
                attachments = [{
                    'type': 'jpeg',
                    'name': 'cover.jpg',
                    'path': cover_art['path']}]
            else:
                attachments = None

            mkv_tracks = []
            # Video tracks are kept unchanged.
            for (count, track_id) in enumerate(playlist.video_tracks):
                mkv_tracks.append({
                    'file_path': playlist.path,
                    'id': track_id,
                    'type': 'video',
                    'properties': {
                        'default': True if count == 0 else False}})

            # Audio tracks are filtered/sorted by language.
            #  Multi-languages tracks are always kept, as it is not possible to
            #  know which languages they contain. The same behavior is applied
            #  for tracks with undetermined language.
            audio_filters = {'language_code': ["mis", "mul", "und"]}
            if args.audio_languages:
                audio_filters['language_code'].extend(args.audio_languages)

            audio_tracks = helpers.filter_tracks(
                playlist.audio_tracks, **audio_filters)
            audio_tracks = helpers.sort_tracks(
                audio_tracks, properties=['language_code'])

            for track_id in audio_tracks:
                mkv_tracks.append({
                    'file_path': playlist.path,
                    'id': track_id,
                    'type': 'audio',
                    'properties': {
                        'default': False}})

            # Subtitle tracks are filtered/sorted by language.
            subtitle_filters = dict()
            if args.subtitle_languages:
                subtitle_filters['language_code'] = args.subtitle_languages

            subtitle_tracks = helpers.filter_tracks(
                playlist.subtitle_tracks, **subtitle_filters)
            subtitle_tracks = helpers.sort_tracks(
                subtitle_tracks, properties=['language_code'])

            # Forced subtitles are identified and filtered by language.
            print("Identifying forced subtitles...")
            forced_subtitles_ids =\
                set(playlist.get_forced_subtitles()) & set(subtitle_tracks)

            for track_id in subtitle_tracks:
                if track_id in forced_subtitles_ids:
                    forced_flag = True
                    # Forced subtitles are tagged to be easily identified on
                    # media players which do not display forced flags.
                    track_name = args.forced_subtitle_names or ''
                else:
                    forced_flag = False
                    track_name = ''

                mkv_tracks.append({
                    'file_path': playlist.path,
                    'id': track_id,
                    'type': 'subtitle',
                    'properties': {
                        'default': False,
                        'forced': forced_flag,
                        'name': track_name}})

            mkv_file_name =\
                str(destination_directory / "{}.mkv".format(args.title))

            # Convert the playlist with Mkvmerge.
            print("Convert playlist {}".format(playlist.number))
            bluray_analyzer.mkvmerge_controller.write(
                mkv_file_name,
                mkv_tracks,
                title=args.title,
                attachments=attachments)
    finally:
        # Unmount the Blu-ray disc if it is a disk image.
        if mount_point is not None:
            try:
                utils.unmount_disk_image(str(mount_point))
            except subprocess.CalledProcessError as exc:
                sys.exit("Unable to unmount disk image: {}".format(exc))

            mount_point.rmdir()

if __name__ == '__main__':
    sys.path.append(str(Path(__file__).resolve().parents[1]))

    from blu_mkv import bluray
    from blu_mkv import helpers
    from blu_mkv import utils
    from blu_mkv.ffprobe import FfprobeController
    from blu_mkv.makemkv import MakemkvController
    from blu_mkv.mkvmerge import MkvmergeController

    parser = argparse.ArgumentParser(
        description=(
            "Convert a Blu-ray disc to Matroska file."
            "Use Ffprobe, Mkvmerge and optionally Makemkv for 3D support."))
    parser.add_argument(
        'title',
        help="Movie title and file name for the Matroska file.")
    parser.add_argument(
        'src_disc',
        help="Blu-ray source. Can be a disk image or directory.")
    parser.add_argument(
        'dst_dir',
        help="Destination directory for the Matroska file.")
    parser.add_argument(
        '-pc', '--playlists_count',
        type=int, default=3,
        help=(
            "Set the maximum number of movie playlists to convert. "
            "Defaults to 3. If set to 0, all movie playlists are converted."))
    parser.add_argument(
        '-al', '--audio_languages',
        type=str, nargs='*',
        help=(
            "Audio tracks to keep according to their language. "
            "Multi-languages tracks or tracks with undetermined language are "
            "always kept."))
    parser.add_argument(
        '-sl', '--subtitle_languages',
        type=str, nargs='*',
        help="Subtitle tracks to keep according to their language.")
    parser.add_argument(
        '-fsn', '--forced_subtitle_names',
        help="Description given to forced subtitle tracks.")
    parser.add_argument(
        '-3d', '--detect_3d',
        action='store_true',
        help="Detect 3D video tracks. Makemkv need to be installed.")

    args = parser.parse_args()
    main(args)
