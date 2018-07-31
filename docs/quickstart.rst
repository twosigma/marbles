Quickstart
==========

Once you have marbles installed, you can run your existing :mod:`unittest` tests with marbles and get marbles failure messages, without changing any code. This lets you switch between marbles and unittest failure messages. For instance, you might want to see marbles failure messages during interactive development and debugging, but see unittest failure messages in CI. To do this

.. code-block:: bash

   $ python -m marbles docs/examples/getting_started.py  # development
   $ python -m unittest docs/examples/getting_started.py  # CI

For example, let's say we have the following :class:`unittest` test case

.. literalinclude:: examples/getting_started.py.original
   :lines: 1-4,33-

If we run this test case with unittest, we'll see a normal unittest failure message

.. literalinclude:: examples/getting_started.txt.original

But, if we run this same test case with marbles instead, we get a marbles failure message, without changing any test code

.. literalinclude:: examples/getting_started.txt


Reading marbles failure messages
--------------------------------

In this section we'll go over the different parts of a marbles failure message.

Source
^^^^^^

Python tracebacks only show the last line of the statement that failed, which can be confusing if the statement that failed spans multiple lines. In a marbles failure message, the "Source" section contains the full assertion statement that failed

.. literalinclude:: examples/getting_started.txt
   :emphasize-lines: 8-13

This doesn't look like a traceback, it looks like code, perhaps even code that I wrote. And, it's a lot easier to recognize than when it's inside a traceback

.. literalinclude:: examples/getting_started.txt.original
   :emphasize-lines: 8

Traceback
^^^^^^^^^

Speaking of the traceback, where is it? Marbles failure messages contain all of the information you would normally find in a traceback (and more), so we can hide the traceback to make failure messages easier to read without losing any information. If you still want to see the traceback, you can run your tests in verbose mode

.. literalinclude:: examples/getting_started.txt.verbose
   :emphasize-lines: 6-10

Locals
^^^^^^

The "Locals" section of a marbles failure messages contains any variables that are in scope at the time the test failed

.. literalinclude:: examples/getting_started.txt
   :emphasize-lines: 14-16

This helps you recover the "state of the world" at the time the test failed and see what the actual and expected runtime values were, without having to put debugging statements in your test code (or even reading or changing your test code at all).

See :ref:`Curating Locals` to see how to control which local variables show up in this section.

Notes
-----

Assertions on :class:`marbles.core.TestCase`\s accept an optional annotation provided by the author. This annotation, if provided, will be included in the failure message.

.. warning:: You can provide annotations to assertions on vanilla :class:`unittest.TestCase`\s *only if* you run them with marbles. If you try to run annotated :class:`unittest.TestCase` tests with unittest they will break.

Let's add an annotation to our example and see what it looks like

.. literalinclude:: examples/getting_started.py.annotated
   :diff: examples/getting_started.py

Now when we run our test, we see an additional section

.. literalinclude:: examples/getting_started.txt.annotated
   :emphasize-lines: 18-20

We go into the :ref:`Note <advanced-note>` annotation in more detail in :ref:`How to win at marbles`.

Writing marbles tests
---------------------

This section will cover how to write :class:`marbles.core.TestCase`\s and how to port :class:`unittest.TestCase`\s to marbles.

To write marbles tests, all you need to do is inherit from :class:`marbles.core.TestCase` wherever you would normally inherit from :class:`unittest.TestCase` and write your test methods exactly as you would normally. Nothing else about your test cases or test methods needs to change (unless you want to add :ref:`annotations <notes>`).

For example, let's take our example test case from earlier

.. literalinclude:: examples/getting_started.py.original
   :lines: 1-4,33-

To turn this into a marbles test case

.. literalinclude:: examples/getting_started.py
   :diff: examples/getting_started.py.original

Now, we get the following output, whether we run our tests with unittest or with marbles

.. literalinclude:: examples/getting_started.txt

.. note:: If you run your tests with ``-m unittest``, the failure message will always include the traceback, even if you don't run your tests in verbose mode. To hide the traceback, you need to run your tests with ``-m marbles``.

Porting unittest tests
^^^^^^^^^^^^^^^^^^^^^^

To replace all of your unittest test cases with marbles test cases

.. code-block:: bash

   find /path/to/files -type f -exec sed -i 's/unittest/marbles.core/g' {} \;

.. warning:: This may not be safe. For example, it will replace ``unittest.mock`` with ``marbles.core.mock``, which doesn't exist. If you use this command, be sure to review the diff.

Don't forget to :ref:`declare marbles as a dependency <Declaring marbles as a dependency>`.

Running tests
-------------

You can run marbles tests exactly like you run vanilla unit tests

.. code-block:: bash

   python -m marbles /path/to/marbles_tests.py
   # -or-
   python -m unittest /path/to/marbles_tests.py

As we saw :ref:`above <Quickstart>`, you can also run vanilla unit tests with marbles and get marbles failure messages, without changing the base class of you test cases

.. code-block:: bash

   python -m marbles /path/to/unittest_tests.py

Marbles also creates a setuptools command so if you are used to running
``python setup.py test``, you can now run:

.. code-block:: bash

    python setup.py marbles

You can go one step further and alias the command test to run marbles
by adding the following to :file:`setup.cfg`:

.. code-block:: bash

    [aliases]
    test = marbles


Declaring marbles as a dependency
---------------------------------

To ensure that marbles is available wherever you need to run your package's unit tests you need to declare :mod:`marbles.core` as a test dependency in your :data:`setup.py` script

.. code-block:: python

   setup(
       ...
       tests_require=[
           'marbles.core'
       ],
       ...
   )
