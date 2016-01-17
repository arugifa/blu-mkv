import subprocess

from blu_mkv import utils


def test_mount_disk_image(mock):
    image_path = '/home/user/downloads/bluray.iso'
    mount_point = '/tmp/user/bluray'

    mock.patch.object(subprocess, 'check_call')
    utils.mount_disk_image(image_path, mount_point)

    subprocess.check_call.assert_called_once_with(
        ['sudo', 'mount', '-o', 'loop', image_path, mount_point])


def test_unmount_disk_image(mock):
    mount_point = '/tmp/user/bluray'

    mock.patch.object(subprocess, 'check_call')
    utils.unmount_disk_image(mount_point)

    subprocess.check_call.assert_called_once_with(
        ['sudo', 'umount', mount_point])
