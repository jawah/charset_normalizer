#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup
from re import search


def get_version():
    with open('charset_normalizer/version.py') as version_file:
        return search(r"""__version__\s+=\s+(['"])(?P<version>.+?)\1""",
                      version_file.read()).group('version')

# Package meta-data.
NAME = 'charset_normalizer'
DESCRIPTION = 'The Real First Universal Charset Detector. No Cpp Bindings, Using Voodoo and Magical Artifacts.'
URL = 'https://github.com/ousret/charset_normalizer'
EMAIL = 'ahmed.tahri@cloudnursery.dev'
AUTHOR = 'Ahmed TAHRI @Ousret'
REQUIRES_PYTHON = '>=3.5.0'
VERSION = get_version()

REQUIRED = [
    'cached_property>=1.5,<2.0',
    'dragonmapper>=0.2,<0.3',
    'prettytable>=1.0,<3.0',
    'loguru>=0.5,<0.6'
]

EXTRAS = {
    'UnicodeDataBackport': ['unicodedata2']
}


here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description.replace(':heavy_check_mark:', '✅'),
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    keywords=['encoding', 'i18n', 'txt', 'text', 'charset', 'charset-detector', 'normalization', 'unicode', 'chardet'],
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    package_data={
        'charset_normalizer': ['assets/frequencies.json', ],
    },
    license='MIT',
    entry_points={
        'console_scripts':
            [
                'normalizer = charset_normalizer.cli.normalizer:cli_detect'
            ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
