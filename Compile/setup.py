from distutils.core import setup
import py2exe, os, re, sys, time

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    windows = [{
            'script': "SilentMapConverter.py",
            "icon_resources": [(0, "icon.ico")]
            }],
    zipfile = None,
    version = "2.0.0",
    name = "SMC",
    description = "Convert SQM into SQF",
)