from distutils.core import setup
import py2exe, os, re, sys

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    windows = [{
            'script': "SilentMapConverter.py",
            "icon_resources": [(0, "icon.ico")]
            }],
    zipfile = None,
    version = "1.0.0",
    name = "SilentMapConverter",
    description = "SQM files in the current folder become SQF files",
)