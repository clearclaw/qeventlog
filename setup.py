#! /usr/bin/env python

try:
  import pyver # pylint: disable=W0611
except ImportError:
  import os, subprocess
  try:
    environment = os.environ.copy()
    cmd = "pip install pyver".split (" ")
    subprocess.check_call (cmd, env = environment)
  except subprocess.CalledProcessError:
    import sys
    print >> sys.stderr, "Problem installing 'pyver' dependency."
    print >> sys.stderr, "Please install pyver manually."
    sys.exit (1)
  import pyver # pylint: disable=W0611

from setuptools import setup, find_packages
import glob

__version__, __version_info__ = pyver.get_version (pkg = "qeventlog",
                                                   public = True)

setup (
    name = "qeventlog",
    version = __version__,
    description = "Celery job event logger ",
    long_description = file ("README.rst").read (),
    classifiers = [
      "Development Status :: 4 - Beta",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: "
      + "GNU General Public License v3 or later (GPLv3+)",
      "Topic :: Utilities",
    ],
    keywords = "celery event logger",
    author = "J C Lawrence",
    author_email = "claw@kanga.nu",
    url = "https://github.com/clearclaw/pyver",
    license = "GPL v3",
    packages = find_packages (exclude = ["tests",]),
    package_data = {"qeventlog": ["_cfgtool/qeventlog",
                                  "_cfgtool/*.templ",
                                  "_cfgtool/install",],
    },
    data_files = [
        ("/etc/cfgtool/module.d/", ["qeventlog/_cfgtool/qeventlog",]),
        ("/etc/qeventlog", glob.glob ("qeventlog/_cfgtool/*.templ")),
        ("./bin", ["qeventlog/qeventlog_manage.py"]),
    ],
    zip_safe = False,
    install_requires = [line.strip ()
                        for line in file ("requirements.txt").readlines ()],
    entry_points = {
        "console_scripts": [
            "qeventlog = qeventlog.main:main",
        ],
    },
)
