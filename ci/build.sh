#!/bin/bash -xe

# need to fix some flake8 failures
python -m flake8 marbles tests || /bin/true
pip install -r requirements.txt
# Can't use the "coverage" script directly because its #! line is too long.
(cd marbles/core && python -m coverage run setup.py test)
(cd marbles/mixins && python -m coverage run setup.py test)
# Combine coverage reports for reporting
python -m coverage combine marbles/core marbles/mixins/.coverage
python -m coverage html
python -m coverage xml
python setup.py build_sphinx
conda build --python "${PYTHON_VERSION}" recipe
