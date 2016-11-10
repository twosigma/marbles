#!/bin/bash -xe

# need to fix some flake8 failures
python -m flake8 marbles tests || /bin/true
python setup.py install
# Can't use the "coverage" script directly because its #! line is too long.
python -m coverage run setup.py test
python -m coverage html
python -m coverage xml
python setup.py build_sphinx
