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


url = 'https://github.com/twosigma/marbles'
setup_dir = os.path.dirname(__file__)

with open(os.path.join(setup_dir, 'marbles/core/VERSION')) as vfile:
    __version__ = vfile.read().strip()

with open(os.path.join(setup_dir, 'classifiers.txt'), 'r') as f:
    classifiers = [line.strip() for line in f.readlines()]

with open(os.path.join(setup_dir, 'README.rst'), 'r') as f:
    long_description = f.read()


setup(
    name='marbles.core',
    version=__version__,
    namespace_packages=[
        'marbles'
    ],
    packages=[
        'marbles',
        'marbles.core'
    ],
    package_dir={
        'marbles.core': 'marbles/core'
    },
    package_data={
        'marbles.core': ['VERSION']
    },
    test_suite='tests',
    install_requires=[],
    extras_require={
        'dev': [
            'coverage',
            'flake8',
            'flake8-per-file-ignores'
        ]
    },
    python_requires='>=3.5,<3.8',
    license='MIT',
    description=('A unittest extension that provides additional '
                 'information on test failure'),
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Jane Adams, Leif Walsh',
    author_email='jane@twosigma.com, leif@twosigma.com',
    url=url,
    project_urls={
        'Documentation': 'https://marbles.readthedocs.io',
        'Source': url,
        'Tracker': '{url}/issues'.format(url=url)
    },
    classifiers=classifiers
)
