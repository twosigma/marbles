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


setup(
    name='marbles',
    version='0.8.0',
    setup_requires=[
        'Sphinx',
        'sphinx_rtd_theme'
    ],
    install_requires=[
        'marbles.core',
        'marbles.mixins'
    ],
    author=[
        'Jane Adams',
        'Leif Walsh'
    ],
    author_email=[
        'jane@twosigma.com',
        'leif@twosigma.com'
    ],
    description='Write better tests, read better test failures',
    url='https://gitlab.twosigma.com/jane/marbles'
)
