#!/usr/bin/env python

#*********************************************************************
# WebTornadoDS: Tango DS to launch a Tornado Web server and generate web report
#
# Author(s): Daniel Roldan <droldan@cells.es>,
#            Manuel Broseta <mbroseta@cells.es>
#
# Copyright (C) 2017, CELLS / ALBA Synchrotron
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import setup, find_packages


classifiers = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 5 - Production/Stable',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: GNU Library or Lesser General Public ' + \
    'License (LGPLv3)',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2.7',
]

__version = '1.0.0'
name = 'WebTornadoDS'
packages = find_packages()
description = 'Tango device server to manage the a tornado Web Server and ' \
              'generate web reports from Tango Attributes'

entry_points = {
    'console_scripts': [
        'WebTornadoDS = WebTornadoDS.server:run',
    ]}

setup(name=name,
      version=__version,
      description= description,
      author='droldan',
      author_email='droldan@cells.es',
      url='',
      packages=packages,
      entry_points=entry_points,
      platforms='all',
      include_package_data=True, #Force read MANIFEST.in
      install_requires=['setuptools', 'python', 'tornado', 'fandango'],
      requires=[],
      classifiers=classifiers
      )