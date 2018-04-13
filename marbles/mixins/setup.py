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
                       'marbles/mixins/VERSION')) as vfile:
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
        'pandas<0.21,>=0.19.1',
        'numpy<1.14,>=1.12.1'
    ],
    tests_require=tests_require,
    extras_require=extras_require,
    description=('Semantically-rich assertions for use '
                 'in marbles and unittest test cases'),
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
