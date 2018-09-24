#
#  Copyright (c) 2018 Two Sigma Open Source, LLC
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#

import os.path
from setuptools import setup


version = '0.10.0'
url = 'https://github.com/twosigma/marbles'
setup_dir = os.path.dirname(__file__)

with open(os.path.join(setup_dir, 'classifiers.txt'), 'r') as f:
    classifiers = [line.strip() for line in f.readlines()]

with open(os.path.join(setup_dir, 'README.rst'), 'r') as f:
    long_description = f.read()

setup(
    name='marbles',
    version=version,
    install_requires=[
        'marbles.core',
        'marbles.mixins'
    ],
    extras_require={
        'dev': [
            'releases',
            'Sphinx',
            'sphinx_rtd_theme'
        ]
    },
    author='Jane Adams, Leif Walsh',
    author_email='jane@twosigma.com, leif@twosigma.com',
    description='Read better test failures',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='MIT',
    url=url,
    download_url='{url}/archive/{version}.tar.gz'.format(url=url,
                                                         version=version),
    project_urls={
        'Documentation': 'https://marbles.readthedocs.io',
        'Source': url,
        'Tracker': '{url}/issues'.format(url=url)
    },
    classifiers=classifiers
)
