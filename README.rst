.. image:: marbles.svg
   :height: 150px
   :width: 150px
   :align: right

=======
marbles
=======

.. image:: https://img.shields.io/pypi/v/marbles.svg
        :target: https://pypi.python.org/pypi/marbles

.. image:: https://img.shields.io/travis/twosigma/marbles.svg
        :target: https://travis-ci.org/twosigma/marbles

.. image:: https://readthedocs.org/projects/marbles/badge/?version=latest
        :target: https://marbles.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://codecov.io/gh/twosigma/marbles/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/twosigma/marbles

Read better test failures.

* Free software: MIT license
* Documentation: https://marbles.readthedocs.io

Overview
--------

`marbles` is a Python `unittest` extension that allows test authors to write
richer tests that expose more information on test failure to help you debug
failing tests faster.

* Treat test failures as documentation
* Contextualize failures without digging through test code
  and dropping debugging statements everywhere
* Write clearer, more explicit tests

Features
--------

* Drop-in `unittest` replacement
* Information-rich failure messages

  * The full statement that failed (instead of just the last line)
  * Local variables in scope at the time the test failed
  * Optional annotation provided by the test author with details about the test
  * Ability to toggle traceback

* Semantically-rich assertion methods
* Assertion logging

Demo
----

You can run the example tests provided to see what a `marbles` failure message
looks like

.. image:: getting_started.png

You can also run your existing `unittest` tests with `marbles`

.. code-block:: bash

   python -m marbles test_module.py

Marbles also creates a setuptools command so if you are used to running
``python setup.py test``, you can now run:

.. code-block:: bash

    python setup.py marbles

You can go one step further and alias the command test to run marbles
by adding the following to :file:`setup.cfg`:

.. code-block:: bash

    [aliases]
    test = marbles

Installing
----------

.. code-block:: bash

   pip install marbles
