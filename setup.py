#!/usr/bin/env python

from setuptools import setup, find_packages
import glob
import os

os.system('pyrcc5 limestorelib.qrc -o limestorelib/resource.py')

datas = [('/usr/share/applications', ['lime-store.desktop','lime-upmanager.desktop']),
        ('/etc/skel/.config/autostart', ['lime-upmanager.desktop']),
        ('/usr/share/pixmaps/', ['apps/lime-store.png','apps/lime-update-manager.png']),
        ('/usr/share/Lime-Store/diller',glob.glob("diller/*.ts")),
        ('/usr/share/Lime-Store/apps',glob.glob("apps/*.svg"))]

setup(
    name = "LimeLinux-Store",
    scripts = ["lime-store","lime-upmanager"],
    packages = find_packages(),
    version = "0.0",
    license = "GPL v3",
    description = "LimeLinux Store And Update Manager",
    author = "Fatih KAYA",
    author_email = "sonakinci41@gmail.com",
    url = "https://github.com/sonakinci41/LimeLinux-Store",
    keywords = ["PyQt5"],
    data_files = datas
)
