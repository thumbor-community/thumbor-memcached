#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of thumbor-memcached.
# https://github.com/thumbor-community/thumbor-memcached

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2015, Bernardo Heynemann <heynemann@gmail.com>

from setuptools import setup, find_packages
from thumbor_memcached import __version__

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'sphinx',
]

setup(
    name='thumbor-memcached',
    version=__version__,
    description='thumbor-memcached provides storages using memcached as a backend.',
    long_description='''
thumbor-memcached provides storages using memcached as a backend.
''',
    keywords='memcache memcached thumbor storage',
    author='Bernardo Heynemann',
    author_email='heynemann@gmail.com',
    url='https://github.com/thumbor-community/thumbor-memcached',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'thumbor',
        # for mac os users, make sure to run:
        # brew install memcached libmemcached
        'pylibmc',
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
