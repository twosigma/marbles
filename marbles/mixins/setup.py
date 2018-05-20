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


with open(os.path.join(os.path.dirname(__file__),
                       'marbles/mixins/VERSION')) as vfile:
    __version__ = vfile.read().strip()

setup_requires = [
    'coverage',
    'flake8',
    'flake8-per-file-ignores'
]

tests_require = [
    'coverage'
]

extras_require = {
    'dev': list(set(setup_requires + tests_require))
}

setup(
    name='marbles.mixins',
    version=__version__,
    namespace_packages=[
        'marbles'
    ],
    packages=[
        'marbles.mixins'
    ],
    package_dir={
        'marbles.mixins': 'marbles/mixins'
    },
    package_data={
        'marbles.mixins': ['VERSION'],
    },
    test_suite='tests',
    setup_requires=setup_requires,
    install_requires=[
        'pandas<0.21,>=0.19.1'
    ],
    tests_require=tests_require,
    extras_require=extras_require,
    license='MIT',
    description=('Semantically-rich assertions for use '
                 'in marbles and unittest test cases'),
    author='Jane Adams, Leif Walsh',
    author_email='jane@twosigma.com, leif@twosigma.com',
    url='https://github.com/twosigma/marbles'
)
