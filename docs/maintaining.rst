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

Maintaining the Changelog
-------------------------

The marbles :doc:`changelog` is maintained by the Sphinx plugin
`releases`_, and its source is in :file:`docs/changelog.rst`.

Most pull requests should add an item to the `changelog
<https://github.com/twosigma/marbles/blob/master/docs/changelog.rst>`__,
at the top, either a bug, feature, or support note.

.. note::

   `releases`_ is clear about the distinction between bugs and other
   release notes. Bugs are included in the next patch version that
   appears above them, while features aren't included until the next
   major or minor version above them. The decision of whether to note
   a change as a bug, feature, or support item will affect where it
   appears in the log, though this can be controlled with the keywords
   ``major`` (put bugs in the next major or minor release), and
   ``backported`` (put features in the next bugfix release).

   See `Release organization
   <http://releases.readthedocs.io/en/latest/concepts.html#release-organization>`__
   for details.

Right before releasing a new version of marbles, add a release item to
the top of the `changelog
<https://github.com/twosigma/marbles/blob/master/docs/changelog.rst>`__
noting the version string and release date, then follow the below
instructions on `Releasing a new version`_.

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

.. note::

   Make sure you've groomed the :doc:`changelog` before tagging a new
   release. See `Maintaining the Changelog`_ for details.

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

You can read a digression about why we bump all the versions at the
same time below, in `Versioning philosophy`_.

Uploading to PyPI
-----------------

Once you've tagged the latest version of marbles, pull from GitHub to
make sure your clone is up to date and clean, build both ``sdist`` and
``wheel`` packages for all three packages, and upload them with
`twine`_. We have a `tox`_ rule to automate building and uploading::

    $ tox -e pypi

.. _pipenv: https://docs.pipenv.org
.. _flake8: http://flake8.pycqa.org
.. _tox: https://tox.readthedocs.io
.. _releases: http://releases.readthedocs.io
.. _bumpversion: https://github.com/peritus/bumpversion
.. _twine: https://github.com/pypa/twine

Versioning philosophy
---------------------

Marbles publishes two subpackages, :mod:`marbles.core` and
:mod:`marbles.mixins`, and a metapackage depending on both,
:mod:`marbles`. This allows users to install or depend on only one of
the subpackages, and also suggests that anyone can publish their own
mixins package.

This raises the question of how to version each of these three
packages.

 1. Release new versions of :mod:`marbles.core` and
    :mod:`marbles.mixins` independently, and have the :mod:`marbles`
    package basically only ever have one release, ``1.0.0``, since it
    doesn't actually change over time.

 2. Give the :mod:`marbles` package a new version each time either
    subpackage gets one, to make it feel like we're moving
    forward.

 3. Release all three packages with the same version string each time
    any of them gets a new release.

`Jupyter <https://pypi.org/project/jupyter/>`_ takes the first
approach, but keep in mind that Jupyter is a much larger project with
distinct teams working on each component, so allowing subpackages to
have independent release schedules makes more sense for that
community.

The second approach has the problem that if we release the subpackages
independently, it's unclear how to version the metapackage when that
happens. Taking the max of the subpackage version strings doesn't work
if the subpackage with a lower one gets an update by itself. There are
a couple other possiblities here, but none of them seemed right.

The third approach, updating everything in lock-step, is what we've
chosen. This will create multiple versions of one or the other package
that are identical, in some cases, which is a little odd. However, it
has the benefit of documenting which versions of :mod:`marbles.core`
and :mod:`marbles.mixins` were reviewed and tested together and
therefore can be expected to work together. It still allows users to
install (and update) them independently, but encourages users of both
to update them together.
