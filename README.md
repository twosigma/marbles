# marbles

`marbles` is a small `unittest` extension by [Jane Adams](mailto:jane@twosigma.com) and [Leif Walsh](mailto:leif@twosigma.com) that allows test authors to provide additional information to test consumers on test failure.

## Background

Two Sigma needs to make assertions about different resources, e.g., directories, files, pandas DataFrames, etc. These are generally referred to as "sanity checks". Python's builtin `unittest` package is a natural framework for expressing these assertions. That being said, testing functionality (which is what `unittest` is designed to do) is different than testing data. If an assertion about a piece of functionality fails, you go inspect the code that defines that functionality. If an assertion about data fails, it's usually not as obvious what you should do. It's also not usually as obvious how data should function, i.e., what data failure even looks like. This is where marbles comes in:

1. expose relevant, actionable information when tests fail
2. improve and codify knowledge, understanding, and expectations of data

By requiring that test authors better understand and codify the ways in which data can fail, marbles helps catch more data failures; by requiring test authors to provide instructions on how to mitigate those failures, marbles helps more people productively respond to those failures.

# Installing

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

# Developing

Create a conda environment and do a development install into it

```bash
conda create --yes --name marbles-dev --file requirements.txt
source activate marbles-dev
python setup.py develop
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
cd build/coverage/htmls; python -m http.server 8080
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
