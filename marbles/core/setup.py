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

import os.path
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__),
                       'marbles/core/VERSION')) as vfile:
    __version__ = vfile.read().strip()

setup_requires = [
    'coverage',
    'flake8'
]

tests_require = [
    'coverage'
]

extras_require = {
    'dev': list(set(setup_requires + tests_require))
}

setup(
    name='marbles.core',
    version=__version__,
    namespace_packages=[
        'marbles'
    ],
    packages=[
        'marbles.core'
    ],
    package_dir={
        'marbles.core': 'marbles/core'
    },
    package_data={
        'marbles.core': ['VERSION']
    },
    test_suite='tests',
    setup_requires=setup_requires,
    install_requires=[],
    tests_require=tests_require,
    extras_require=extras_require,
    description=('A unittest extension that provides additional '
                 'information on test failure'),
    author=[
        'Jane Adams',
        'Leif Walsh'
    ],
    author_email=[
        'jane@twosigma.com',
        'leif@twosigma.com'
    ],
    url='https://gitlab.twosigma.com/jane/marbles'
)
