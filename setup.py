#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from tvdbrest import VERSION

setup(
    name='tvdb-rest',
    version=VERSION,
    description='Python client implementation for The TVDB REST API',
    author='Johann Schmitz',
    author_email='johann@j-schmitz.net',
    url='https://code.not-your-server.de/tvdb-rest.git',
    download_url='https://code.not-your-server.de/tvdb-rest.git/tags/%s.tar.gz' % VERSION,
    packages=find_packages(exclude=('tests',)),
    zip_safe=False,
    license='GPL-3',
)
