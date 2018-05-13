.. marbles documentation master file, created by
   sphinx-quickstart on Sat Sep  3 19:46:28 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the marbles documentation!
=====================================

Marbles is a :mod:`unittest` extension that allows test authors to write richer tests that expose more information on test failure. You can use marbles anywhere you use unittest to get better failure messages that help you debug failing tests faster.


.. code-block:: bash

   $ python -m marbles hello_world.py
   F
   ======================================================================
   FAIL: test_hello_world (hello_world.HelloWorldTestCase)
   ----------------------------------------------------------------------
   marbles.core.marbles.ContextualAssertionError: 'Hello, world!' != 'Bonjour, le monde!'
   - Hello, world!
   + Bonjour, le monde!


   Source (hello_world.py):
        11
    >   12 self.assertEqual(english, french, note=note)
        13
   Locals:
           english=Hello, world!
           french=Bonjour, le monde!
   Note:
           Welcome to your first marbles test!


   ----------------------------------------------------------------------
   Ran 1 test in 0.002s

   FAILED (failures=1)

Philosophy
----------

The main idea behind marbles is that test failures are documentation. We wanted failure messages that put failures in context and clearly communicate the author's intent with each test. We wanted failure messages that give test consumers enough information that they don't have to dig through test code to understand what's going on. And, we wanted test authors to start thinking about test failures as documentation *for test consumers*, whether that's them in a few months or someone completely new to to the test suite, to help everyone get in the habit of writing better, clearer tests.


Contents
--------

User Guide
""""""""""
.. toctree::
   :maxdepth: 3

   install
   quickstart
   winning

Developer Guide
"""""""""""""""
.. toctree::
   :maxdepth: 3

   contributing

Reference
"""""""""
.. toctree::
   :maxdepth: 3

   reference

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

