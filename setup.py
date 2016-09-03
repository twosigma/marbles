from setuptools import setup

from marbles import __version__


def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name='marbles',
    packages=[
            'marbles',
        ],
    test_suite='tests',
    version=__version__,
    description='a small unittest extension that provides additional information on test failure',
    long_description=readme(),
    author=['Jane Adams', 'Leif Walsh'],
    author_email=['jane@twosigma.com', 'leif@twosigma.com'],
    url='https://gitlab.twosigma.com/jane/marbles'
    )

