#!/usr/bin/env python

from setuptools import setup, find_packages


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
      install_requires=['setuptools','python',
                        'tornado','fandango'],
      requires=[],
      )