import subprocess


def mount_disk_image(image_path, mount_point):
    """Mount disk image with sudo permissions.

    :param str image_path: disk image's path
    :param str mount_point: directory's path where to mount the disk image
    """
    subprocess.check_call([
        'sudo',
        'mount',
        '-o', 'loop',
        image_path,
        mount_point])


def unmount_disk_image(mount_point):
    """Unmount file system with sudo permissions.

    :param str mount_point: directory's path where the file system is mounted
    """
    subprocess.check_call([
        'sudo',
        'umount',
        mount_point])
