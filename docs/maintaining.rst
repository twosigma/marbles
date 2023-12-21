.. highlight:: shell

==================
Maintainer's Guide
==================

This page documents some common workflows for maintaining
marbles. Most of these are also useful when developing marbles.

Environment
-----------

Marbles comes with a :file:`requirements/dev.txt` file you can use to create
a virtualenv for developing. To get started, just install from this
requirements file in a virtualenv::

    $ pip install -r requirements/dev.txt

.. note::

    If you're using our VS Code devcontainer, you can skip this step: all the
    tools you need will be installed by default in your environment.

Adding new packages
~~~~~~~~~~~~~~~~~~~

You can tentatively add packages to your environment as normal, with ``pip
install``. These will only affect your own environment, but you can try them
out by running ``python -m unittests discover ...`` to see if they work.

When you're ready to commit to using them, add them to the appropriate ``*.in``
file in :file:`requirements/`, or if they're going to be new runtime
dependencies, either :file:`marbles/core/setup.cfg` or
:file:`marbles/mixins/setup.cfg`. Then resolve them to concrete dependencies
with::

    $ nox -s pip_compile

This will make those new dependencies available to the `nox`_ environments.
More on `nox`_ below.

After this, add and commit all :file:`requirements/*.txt` and
:file:`*/requirements.txt` files and include them in your pull request.

Linting
-------

You can lint the code with `flake8`_::

    $ nox -s flake8

Tests
-----

You can run the tests for either :mod:`marbles.core` or
:mod:`marbles.mixins` separately, in either subpackage's directory::

    $ python -m unittest discover tests

You can run all the tests with `nox`_::

    $ nox -s test

Coverage
--------

Since the marbles tests are split across the subpackages, checking
coverage isn't very straightforward, but we've configured `nox`_ to do
it for you::

    $ nox -s coverage

If you want to look at the source code annotated with coverage
metrics, this produces an HTML report you can view. You can serve it locally::

    $ nox -s serve_coverage

Documentation
-------------

You can build the docs and view them locally::

    $ nox -s docs

Similarly, you can serve them for local viewing::

    $ nox -s serve_docs

Automation with `nox`_
----------------------

We use `nox`_ to run continuous integration builds for multiple versions of
Python and on multiple platforms in GitHub Actions, and to run each piece of
our continuous integration in a separate virtualenv. You can do this locally
too, to make sure your change will build cleanly.

We've configured `nox`_ to be able to:

1. Run all the tests with Python 3.9, 3.10, 3.11, and 3.12

2. Measure and report on code coverage

3. Lint the code with `flake8`_

4. Build the documentation

If you just run :program:`nox` by itself, it will run tests and linting,
each in its own virtualenv::

    $ nox

You can also run a subset of these with ``-s``::

    $ nox -s docs
    $ nox -s test-3.9
    $ nox -s flake8 coverage-3.9

VS Code Tasks
~~~~~~~~~~~~~

We provide several VS Code tasks that can run common things you'll want to run
while developing.

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

1. :file:`setup.cfg`

2. :file:`marbles/core/marbles/core/VERSION`

3. :file:`marbles/mixins/marbles/mixins/VERSION`

In addition, when we bump the version, we do so in an isolated commit,
and tag that commit with the version number as well.

.. note::

   Make sure you've groomed the :doc:`changelog` before tagging a new
   release. See `Maintaining the Changelog`_ for details.

We use `bump2version`_ to automate this. To run `bump2version`_, you
need to be in a clean git tree (don't worry, it will complain to you
if that's not the case).

You can increase either the ``major``, ``minor``, or ``patch``
version::

    $ nox -s bumpversion -- major
    $ nox -s bumpversion -- minor
    $ nox -s bumpversion -- patch

This will update the version strings in all the above files and commit
that change, but won't tag it. You should create a pull request for
the version update, merge it (without squashing it into other
commits), and then tag it once it's on the ``main`` branch:
https://github.com/twosigma/marbles/releases/new.

You can read a digression about why we bump all the versions at the
same time below, in `Versioning philosophy`_.

Uploading to PyPI
-----------------

Once you've tagged the latest version of marbles, pull from GitHub to
make sure your clone is up to date and clean, build both ``sdist`` and
``wheel`` packages for all three packages, and upload them with
`twine`_. We have `nox`_ sessions to automate building and uploading::

    $ nox -s package
    $ nox -s upload

.. _flake8: http://flake8.pycqa.org
.. _nox: https://nox.thea.codes/en/stable
.. _releases: http://releases.readthedocs.io
.. _bump2version: https://github.com/c4urself/bump2version
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
