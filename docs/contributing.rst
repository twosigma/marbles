.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/twosigma/marbles/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

The `issue templates <https://github.com/twosigma/marbles/issues/new/choose>`__
will tell you how to collect version information.

Fix Bugs
~~~~~~~~

Look through the `GitHub issues <https://github.com/twosigma/marbles/issues>`__
for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants
to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the `GitHub issues <https://github.com/twosigma/marbles/issues>`__
for features. Anything tagged with "enhancement" and "help wanted" is open to
whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

marbles could always use more documentation, whether as part of the
official marbles docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/twosigma/marbles/issues/new/choose.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.

Build a Plugin
~~~~~~~~~~~~~~

We've developed marbles in a pluggable way, so you can contribute to the marbles
ecosystem without committing code to the marbles repo!

Just as marbles provides some mixins you can add to a :class:`unittest.TestCase`
by adding a superclass to your test, you can develop more mixins outside the
marbles repo and publish them yourself, they'll interoperate just fine. Of
course, we'd like to include mixins which may be useful to many people in the
:mod:`marbles.mixins` package, so if you think that's the case, please send us a
pull request.

The marbles annotation logging mechanism right now just writes JSON structured
data to a file. You can use ``logstash``, ``mongoimport``, ``Spark``, or any
other tool that understands JSON to store and analyze them after the fact. But,
you can also implement the marbles logging interface to do something else with
the assertion metadata, instead of logging it to disk. If you'd like to share
your logging plugin, or discuss ideas for how to build one, just open an issue
and we can discuss it with you there.

Get Started!
------------

Ready to contribute? Here's how to set up marbles for local development.

Using Devcontainers
~~~~~~~~~~~~~~~~~~~

We provide a
`devcontainers <https://code.visualstudio.com/docs/remote/containers>`__ config
that should get you a working development environment with one gesture. If
you're new to devcontainers, make sure you have `VS
Code <https://code.visualstudio.com/>`__ installed with the `Remote
Containers <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers>`__
extension.

Use the ``Remote-Containers: Clone Repository in Container Volume...`` action in
VS Code to clone the ``twosigma/marbles`` repo. It will set up your development
environment so you can run ``nox`` and start coding straight away.

Using Codespaces
~~~~~~~~~~~~~~~~

You can also try this environment in
`Codespaces <https://github.com/features/codespaces>`__ by creating a codespace
from the `marbles repo homepage <https://github.com/twosigma/marbles>`__\ .

Developing on Your Own Machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Fork the marbles repo on GitHub `here
   <https://github.com/twosigma/marbles/fork>`__.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/marbles.git

3. Install your local copy into a virtualenv. You can run::

    $ pip install -r requirements/dev.txt
    $ pip install -e marbles/core -e marbles/mixins

   This will install all of the ``marbles`` development dependencies,
   and install ``marbles`` in development mode, so your changes to the
   files in your clone will take effect immediately, and put you in a
   shell where you can run the tests, build the docs, etc.

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature-or-docs

   Now you can make your changes locally. ``marbles`` is developed as separate
   packages in the namespace package ``marbles``:

   1. The :class:`~unittest.TestCase` customizations and the assertion logging
      infrastructure live in :mod:`marbles.core`, which you'll find inside the
      repo under :file:`marbles/core`.
   2. The mixins live in :mod:`marbles.mixins`, which you'll find inside the
      repo under :file:`marbles/mixins`.

5. As you make changes, you can run the tests and lint with
   flake8::

    $ nox

   To separately lint or run tests, specify a session::

    $ nox -s flake8
    $ nox -s test

   .. note:: Don't worry about bumping version numbers yourself. We'll
             handle this in the release that includes your changes.

   For more developer workflows (linting, testing, test coverage,
   docs), see :doc:`maintaining`.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

8. We'll review your changes, merge them, and include them in the next
   release.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Make
   sure your new functionality is documented with docstrings and appropriate
   additions to the Sphinx docs, and add the feature to the list in README.md.
3. The pull request should work for Python 3.9, 3.10, 3.11, and 3.12, and on
   Linux, Windows, and OS X. You'll see those checks run in your pull request.
4. In order to accept your code contributions, please fill out the appropriate
   Contributor License Agreement in the `cla folder
   <https://github.com/twosigma/marbles/tree/master/cla>`__ and submit it to
   tsos@twosigma.com. We need this before we can accept your pull request.
