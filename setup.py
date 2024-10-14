from distutils.core import setup
from py2exe import freeze

freeze(windows=['main.py'], options={'bundle_files': 1})