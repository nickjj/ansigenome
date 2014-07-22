#!/usr/bin/env python

import sys

try:
    from setuptools import setup
except ImportError:
    print "Ansigenome needs setuptools in order to build. " + \
          "Install it using your package manager " + \
          "(usually python-setuptools) or via pip (pip install setuptools)."
    sys.exit(1)

setup(name="ansigenome",
      version=open("VERSION", "r").read()[:-1],
      author="Nick Janetakis",
      author_email="nick.janetakis@gmail.com",
      url="https://github.com/nickjj/ansigenome",
      description="A tool to help you gather information and " +
      "manage your Ansible roles.",
      license="GPLv3",
      install_requires=["jinja2", "PyYAML", "setuptools"],
      packages=["ansigenome"],
      scripts=["bin/ansigenome"],
      data_files=[])
