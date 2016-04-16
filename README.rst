=======
Blu-MKV
=======

.. image:: https://travis-ci.org/alexandre-figura/blu-mkv.svg?branch=master
    :target: https://travis-ci.org/alexandre-figura/blu-mkv

**Blu-MKV** is a Python script and library which goal is to convert Blu-ray discs to Matroska (MKV) files. It is based upon existing tools: **Ffprobe**, **Mkvmerge** and **Makemkv**. You could just use these latter to manually remux your Blu-ray discs, but **Blu-MKV** will make the task easier and give you more free time to watch and enjoy your movies.


Examples
========

You can simply convert a Blu-ray disc to MKV as follows::

    $ blu-mkv/scripts/convert_bluray_to_mkv.py "Holiday Movie" ~/bluray.iso ~/Videos/

This will remux ``~/bluray.iso`` into ``~/Videos/Holiday Movie.mkv``, and set the MKV's title to **Holiday Movie**. Blu-ray discs can be either disk images or directories.

Advanced options are also available. Hence, you could choose to only keep english audio tracks and french subtitles::

    $ blu-mkv/scripts/convert_bluray_to_mkv.py "Holidays Movie" ~/bluray.iso ~/Videos/ --audio_languages eng --subtitle_languages fre

A list of all available options and their description is available::

    $ blu-mkv/scripts/convert_bluray_to_mkv.py --help


Installation
============

Prerequisites
-------------

In order to use **Blu-MKV**, you have to install first:

- Python >= 3.4
- Mkvmerge >= 8.7
- Ffprobe >= 2.8
- OpenJDK 7, for analyzing discs with BD-J content
- sudo, for mounting/unmounting disk images

Optionally, if you want to add support for 3D titles, you also need:

- Makemkv >= 1.9

Please note that 3D titles are only identified: their conversion is currently not supported (but planned).


Minimal Installation
--------------------

**Blu-MKV** requires external Python packages to work. Hence, you also have to install:

- Pip (also known as *python-pip*), a tool for installing Python packages

Then, you can install the **Blu-MKV**'s dependencies::

    $ pip install -r blu-mkv/requirements.txt


Recommended Installation
------------------------

The previous installation method has a major drawback: **Blu-MKV**'s dependencies are installed globaly on your machine. This can lead to some conflicts, for example, when other Python projects require the same packages but in different versions.

Hence, it is strongly advised to create an isolated environment for **Blu-MKV**. This can be done by installing first:

- Pip (also known as *python-pip*), a tool for installing Python packages
- Virtualenvwrapper (also known as *python-virtualenvwrapper*), a tool for working with isolated environments

Then, configure your ``.bashrc`` (or *bashrc-like*) to load **virtualenvwrapper** stuff automatically when you open a new shell::

    $ echo "source $(which virtualenvwrapper.sh)" >> ~/.bashrc
    $ source ~/.bashrc

You can now create an isolated Python environment and install dependencies required by **Blu-MKV**::

    $ mkvirtualenv blu-mkv
    $ pip install -r blu-mkv/requirements.txt

Each time you will want to convert a Blu-ray disc, you have to enable the Python environment before::

    $ workon blu-mkv
    $ blu-mkv/scripts/convert_bluray_to_mkv.py ...


System Configuration
--------------------

You need to have the permissions to mount and unmount file systems if you plan to convert Blu-ray discs stored into disk images. For example, add these lines to your sudoers file::

    Cmnd_Alias MOUNT = /usr/bin/mount, /usr/bin/umount
    your_username ALL=(ALL) NOPASSWD: MOUNT

It is strongly advised to set the ``NOSPASSWD`` directive or to increase the default password prompt timeout. Indeed, if you miss to enter your password at the end of the conversion, **Blu-MKV** will fail to unmount the disk image.


Code Reuse
==========

**Blu-MKV** also provides a set of classes that you can reuse to create your own scripts. In particular, you will find in:

- ``blu_mkv/bluray.py``: a ``BlurayAnalyzer`` to probe Blu-ray discs
- ``blu_mkv/makemkv.py``, ``blu_mkv/mkvmerge.py`` and ``blu_mkv/ffprobe.py``: controllers to interface with tools of the same name

You can have a look at the existing script to better understand how these classes tie together.


Contribution
============

Bug reports or new feature requests can be submitted on Github_. Also, you are more than welcome to contribute to this project by sending `Pull Requests`_.

.. _Github: https://github.com/alexandre-figura/blu-mkv/issues
.. _Pull Requests: https://github.com/alexandre-figura/blu-mkv/pulls
