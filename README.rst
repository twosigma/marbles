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

Read better test failures.

* Free software: MIT license
* Documentation: https://marbles.readthedocs.io.

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

Demo
----

You can run the example tests provided to see what a `marbles` failure message
looks like

.. code-block:: none

   python -m marbles docs/examples/getting_started.py
   F
   ======================================================================
   FAIL: test_create_resource (docs.examples.getting_started.ResponseTestCase)
   ----------------------------------------------------------------------
   marbles.core.marbles.ContextualAssertionError: 409 != 201

   Source (/path/to/docs/examples/getting_started.py):
        39 res = requests.put(endpoint, data=data)
    >   40 self.assertEqual(
        41     res.status_code,
        42     201
        43 )
   Locals:
           endpoint=http://example.com/api/v1/resource
           data={'name': 'Little Bobby Tables', 'id': 1}


   ----------------------------------------------------------------------
   Ran 1 test in 0.002s

   FAILED (failures=1)

You can also run your existing `unittest` tests with `marbles` in two steps

.. code-block:: bash

   python -m marbles test_module.py

Installing
----------

.. code-block:: bash

   pip install marbles
