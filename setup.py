#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'charset_normalizer'
DESCRIPTION = 'The Real First Universal Charset Detector. Offer a viable solution alternative to Chardet.'
URL = 'https://github.com/ousret/charset_normalizer'
EMAIL = 'ahmed.tahri@cloudnursery.dev'
AUTHOR = 'Ahmed TAHRI @Ousret'
REQUIRES_PYTHON = '>=3.4.0'
VERSION = '0.1.7'

# What packages are required for this module to be executed?
REQUIRED = [
    'cached_property',
    'dragonmapper',
    'zhon',
    'prettytable'
]

# What packages are optional?
EXTRAS = {
    'permit to generate frequencies.json using html data': ['requests_html'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    keywords=['encoding', 'i18n', 'txt', 'text', 'charset', 'charset-detector', 'normalization', 'unicode'],
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
