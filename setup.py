#
#       Copyright (c) 2017 Two Sigma Investments, LP
#       All Rights Reserved
#
#       THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE OF
#       Two Sigma Investments, LP.
#
#       The copyright notice above does not evidence any
#       actual or intended publication of such source code.
#

from setuptools import setup

import versioneer


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='marbles',
    packages=['marbles'],
    test_suite='tests',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    setup_requires=[
        'coverage',
        'flake8',
        'Sphinx',
        'sphinx_rtd_theme'
    ],
    install_requires=[
        'pandas<=0.20.3,>=0.19.1',
        'numpy==1.13.1'
    ],
    tests_require=[
        'coverage'
    ],
    description=('A unittest extension that provides additional '
                 'information on test failure'),
    long_description=readme(),
    author=['Jane Adams', 'Leif Walsh'],
    author_email=['jane@twosigma.com', 'leif@twosigma.com'],
    url='https://gitlab.twosigma.com/jane/marbles'
)
