.. highlight:: shell

==================
Maintainer's Guide
==================

This page documents some common workflows for maintaining
marbles. Most of these are also useful when developing marbles.

Environment
-----------

Marbles comes with a :file:`Pipfile` that `pipenv`_ can use to manage
your virtualenv for developing. To get started, install `pipenv`_ once
for your machine with your package manager of choice::

    $ pip install --user pipenv

Creating your environment
~~~~~~~~~~~~~~~~~~~~~~~~~

In the marbles codebase, create a development virtualenv, and enter
it::

    $ pipenv install --dev
    $ pipenv shell

Inside this environment, you should have everything you need to work
on marbles. See the other sections in this doc for common activities.

Adding new packages
~~~~~~~~~~~~~~~~~~~

If you want to add a new package for development, install it with
`pipenv`_::

    $ pipenv install --dev pylint

This will update the :file:`Pipfile` with :mod:`pylint` as a new
development dependency, and will update :file:`Pipfile.lock` with the
exact version you installed. If this dependency is needed for
something you added to marbles, you should include the changes to both
:file:`Pipfile` and :file:`Pipfile.lock` in your pull
request. Otherwise, please don't include the changes to
:file:`Pipfile` and :file:`Pipfile.lock` in your pull request.

Linting
-------

You can lint the code with `flake8`_::

    $ python -m flake8

Tests
-----

You can run the tests for either :mod:`marbles.core` or
:mod:`marbles.mixins` separately::

    $ python marbles/core/setup.py test
    $ python marbles/mixins/setup.py test

Coverage
--------

Since the marbles tests are split across the subpackages, checking
coverage isn't very straightforward, but we've configured `tox`_ to do
it for you (more on `tox`_ below)::

    $ tox -e coverage

If you want to look at the source code annotated with coverage
metrics, this produces an HTML report you can view, by loading
file:///path/to/marbles/build/coverage/html/index.html in your
browser.

Documentation
-------------

You can build the docs and view them locally::

    $ python setup.py build_sphinx

Then, load file:///path/to/marbles/build/sphinx/html/index.html in
your browser. If you make changes to just docstrings, but not
:file:`.rst` files, Sphinx may not rebuild those docs, you can
embolden it to do so with these options::

    $ python setup.py build_sphinx -Ea

Automation with `tox`_
----------------------

We use `tox`_ to run continuous integration builds for multiple
versions of Python, and to run each piece of our continuous
integration in a separate virtualenv. You can do this locally too, to
make sure your change will build cleanly on Travis CI.

We've configured `tox`_ to be able to:

1. Run all the tests with Python 3.5 and 3.6

2. Measure and report on code coverage

3. Lint the code with `flake8`_

4. Build the documentation

If you just run :program:`tox` by itself, it will do all of the above,
each in its own virtualenv::

    $ tox

You can also run a subset of these with ``-e``::

    $ tox -e docs
    $ tox -e py36
    $ tox -e flake8,coverage

Releasing a new version
-----------------------

The marbles meta-package and subpackage version strings are stored in
a few different locations, due to the namespace package setup:

1. :file:`setup.py`

2. :file:`setup.cfg`

3. :file:`marbles/core/marbles/core/VERSION`

4. :file:`marbles/mixins/marbles/mixins/VERSION`

In addition, when we bump the version, we do so in an isolated commit,
and tag that commit with the version number as well.

We use `bumpversion`_ to automate this. To run `bumpversion`_, you
need to be in a clean git tree (don't worry, it will complain to you
if that's not the case).

You can increase either the ``major``, ``minor``, or ``patch``
version::

    $ bumpversion major
    $ bumpversion minor
    $ bumpversion patch

This will update the version strings in all the above files and commit
that change, but won't tag it. You should create a pull request for
the version update, merge it (without squashing it into other
commits), and then tag it once it's on the ``master`` branch:
https://github.com/twosigma/marbles/releases/new.

Uploading to PyPI
-----------------

Once you've tagged the latest version of marbles, pull from GitHub to
make sure your clone is up to date and clean, build both ``sdist`` and
``wheel`` packages for all three packages, and upload them with
`twine`_::

    $ rm -rf dist marbles/{core,mixins}/dist
    $ (cd marbles/core; python setup.py sdist bdist_wheel)
    $ (cd marbles/mixins; python setup.py sdist bdist_wheel)
    $ python setup.py sdist bdist_wheel
    $ twine upload dist/* marbles/{core,mixins}/dist/*

.. _pipenv: https://docs.pipenv.org
.. _flake8: http://flake8.pycqa.org
.. _tox: https://tox.readthedocs.io
.. _bumpversion: https://github.com/peritus/bumpversion
.. _twine: https://github.com/pypa/twine
