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
    setup_requires=['Sphinx', 'sphinx_rtd_theme'],
    description=('a small unittest extension that provides additional '
                 'information on test failure'),
    long_description=readme(),
    author=['Jane Adams', 'Leif Walsh'],
    author_email=['jane@twosigma.com', 'leif@twosigma.com'],
    url='https://gitlab.twosigma.com/jane/marbles'
)
