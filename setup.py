#! /usr/bin/env python

from setuptools import setup, find_packages
import glob, versioneer

setup (
    name = "qeventlog",
    version = versioneer.get_version (),
    description = "Celery job event logger ",
    long_description = file ("README.rst").read (),
    cmdclass = versioneer.get_cmdclass (),
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
    url = "https://github.com/clearclaw/qeventlog",
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
