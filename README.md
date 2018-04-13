# marbles

`marbles` is a Python `unittest` extension by [Jane Adams](mailto:jane@twosigma.com) and [Leif Walsh](mailto:leif@twosigma.com) that allows test authors to write richer tests that expose more information to test consumers on test failure. These information-rich tests help test consumers respond to failures without having to dig into the test code.

# Installing

The `marbles` namespace package contains two packages: `marbles.core` and `marbles.mixins`. `marbles.core` provides test cases that expose more information on test failure. `marbles.mixins` provides a set of semantically-rich assertions for use in both `marbles` and Python `unittest` tests. You can install the `marbles` package as a whole or install each subpackage individually.

You can install `marbles` directly with `setup.py` or using `pip`:

```bash
python setup.py install
# -or-
pip install .
```

You can also install `marbles` directly from GitLab:

```bash
pip install git+https://gitlab.twosigma.com/jane/marbles@<version tag>
```

You can also install `marbles` with conda:

```bash
conda install marbles
```

To install the subpackages individually, you can use `setup.py`:

```bash
cd marbles/core && python setup.py install
# -and/or-
cd marbles/mixins && python setup.py install
```

You can also install the subpackages with conda:

```bash
conda install marbles-core
# -and/or-
conda install marbles-mixins
```

Note that you cannot use `pip` to install subpackages individually or install subpackages individually from GitLab.

# Developing

Create an empty conda environment and install from the requirements.txt file. This will install dependencies and do a development ("editable") install of both of the subpackages.

```bash
conda create --yes --name marbles-dev python
source activate marbles-dev
pip install -r requirements.txt
```

Now you can edit code and run scripts or a Python shell. Imports of marbles modules and packages will come from the current directory, so your changes will take effect.

# Running Tests

Tests are written with the builtin `unittest` package, live in `tests/`, and are run with `setup.py`:

```bash
python setup.py test
```

## Test Coverage

You can get test coverage by running tests under `coverage`:

```bash
coverage run setup.py test
coverage report
```

Instead of `coverage report`'s text output you can get an HTML report including branch coverage information:

```bash
coverage run setup.py test
coverage html
cd build/coverage/html; python -m http.server 8080
```

and then visit [http://localhost:8080](http://localhost:8080).

# Building Documentation

Docs live in `docs/` and can be run with `setup.py`:

```bash
python setup.py build_sphinx
cd build/sphinx/html; python -m http.server 8080
```

and then visit [http://localhost:8080](http://localhost:8080).

# Releases

Version information is pulled from git tags by `versioneer`, so cutting a new release is as simple as tagging and pushing the tag:

```bash
git tag 0.6.9
git push origin 0.6.9
```

Once this tag exists, future package and documentation builds will automatically get that version, and users can `pip install` using that git tag from GitLab:

```bash
pip install git+https://gitlab.twosigma.com/jane/marbles@0.6.9
```

After tagging, you can release a new conda package with [Jenkins](http://tsmerejenkins.app.twosigma.com:8080/job/Datanomics/job/marbles/job/release/).

Other projects can depend on `marbles` using `dependency_links`:

```python
setup(
    ...,
    install_requires=['marbles==0.6.9'],
    dependency_links=['https://gitlab.twosigma.com/jane/marbles@0.6.9#egg=marbles-0.6.9'],
    ...
)
```

# Bugs

Please [open an issue](https://gitlab.twosigma.com/jane/marbles/issues/new?issue) to report any bugs.
