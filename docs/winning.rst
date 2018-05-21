How to win at marbles
=====================

Out of the box, marbles gives you better failure messages, but it also gives you control over what information your failure messages contain. In this section, we'll cover how to write your tests to get the most out of your failure messages.

Curating Locals
---------------

Local variables defined within the test are included in the "Locals" section of the failure message. This helps the test consumer to reconstruct the "state of the world" at the time the test failed. Marbles lets you control which locals will be included in this section.

Excluding Locals
^^^^^^^^^^^^^^^^

Not all local variables will be relevant to the test consumer, and exposing too many locals could be as confusing as exposing too few. If you need to define variables in your test but don't want them to show up in the output, you can exclude them from the "Locals" section by making them internal or name-mangled (prepending them with one or two underscores).

.. note:: The local variables ``self``, ``msg``, and ``note`` are automatically excluded from the "Locals" section.

.. literalinclude:: examples/exclude_locals.py
   :emphasize-lines: 10-11

This will produce the following output. Notice that the variables ``_intermediate_state_1`` and ``__intermediate_state_2`` don't appear in "Locals".

.. literalinclude:: examples/exclude_locals.txt
   :emphasize-lines: 12-14

Locals-only Locals
^^^^^^^^^^^^^^^^^^

Conversely, there may be some local state that you want to expose to the test consumer that your test doesn't actually need to use. We recommend creating local variables for these anyway.

.. note:: Python linters like `flake8`_ will complain about variables that are assigned but never used, but most linters provide ways of ignoring specific lines.

   .. _flake8: http://flake8.pycqa.org/en/latest/

In the example below, even though we don't need to define ``file_name``, it's useful for the test consumer to know *what* file has a size we don't expect. We sidestep the flake8 warning with the comment ``# noqa: F841`` (F841 is the code for "local variable is assigned but never used")

.. literalinclude:: examples/extra_locals.py
   :emphasize-lines: 8

When we run this test, we'll see ``file_name`` in locals

.. literalinclude:: examples/extra_locals.txt
   :emphasize-lines: 13

.. _advanced-note:

Notes
-----

Note annotations are intended to help the test author communicate any context or background information they have about the test. For example, what's the context of the edge case this particular test method is exercising? The note annotation is a good place to put information that doesn't fit into the test method name or into the assertion statement.

Note annotations are accepted in addition to the ``msg`` argument accepted by all assertions. If specified, the ``msg`` is used as the error message on failure, otherwise it will be the standard message provided by the assertion.

The ``msg`` should be used to explain exactly what the assertion failure was, e.g., ``x was not greater than y``, while the ``note`` can provide more information about why it's important that ``x`` be greater than ``y``, why we expect ``x`` to be greater than ``y``, what needs to happen if ``x`` isn't greater than ``y``, etc. The ``note`` doesn't (and in fact shouldn't) explain what the assertion failure *is* because the ``msg`` already does that well.

For example, in the failure message below, the standard message (``409 != 201``) and the note annotation complement each other. The standard message states that the status code we got (``409``) doesn't equal the status code we expected (``201``), while the note provides context about the status code ``409``.

.. literalinclude:: examples/getting_started.txt.annotated
   :emphasize-lines: 6,19-20

.. note::

   We recommend that you bind note annotations to a variable named ``note``, or pass them to assertions directly, so that they're not repeated in the "Locals" section. Otherwise, you'll need to manually exclude them from the "Locals" section. See `Excluding Locals`_ for how to do this.

Dynamic Note
^^^^^^^^^^^^

Note annotations can contain format string fields that will be expanded with local variables if/when the test fails. They're similar to `f-strings`_ in that you don't have to call :meth:`str.format` yourself, but they differ in that they're only expanded if and when your test fails.

.. _f-strings: https://docs.python.org/3/reference/lexical_analysis.html#f-strings

Let's add a format string field to our note annotation

.. literalinclude:: examples/getting_started.py.dynamic
   :diff: examples/getting_started.py.annotated

When this test fails, ``endpoint`` will be formatted into our note string

.. literalinclude:: examples/getting_started.txt.dynamic
   :emphasize-lines: 19-20

Required Note
^^^^^^^^^^^^^

Depending on the complexity of what you're testing, you may want to require that ``note`` be provided for all assertions. If you want to require notes, your test cases should inherit from :class:`marbles.core.AnnotatedTestCase` instead of from :class:`marbles.core.TestCase`. The only difference is that, while ``note`` is optional for assertions on :class:`~marbles.core.TestCase`\s, it's required for all assertions on :class:`~marbles.core.AnnotatedTestCase`\s.

If you don't provide notes to an assertion on an :class:`~marbles.core.AnnotatedTestCase` you'll see an error

.. literalinclude:: examples/required_note.txt

Custom assertions
-----------------

:class:`unittest.TestCase`\s expose several assert methods for use in unit tests. These assert methods range from very straightforward assertions like :meth:`~unittest.TestCase.assertTrue` to the more detailed assertions like :meth:`~unittest.TestCase.assertWarnsRegex`. These assertions allow the test author to clearly and concisely assert their expectations.

marbles.mixins
^^^^^^^^^^^^^^

The :mod:`marbles.mixins` package adds even more assertion methods that you can use, including assertions about betweenness, monotonicity, files, etc. For the most part, :mod:`marbles.mixins` assertions trivially wrap :mod:`unittest` assertions. The reason to use specific assertions is that the semantically-richer method names can give the test consumer valuable information about the predicate being tested, the types of the objects being tested, etc. For example, :meth:`~unittest.TestCase.assertRegex` doesn't tell you anything about the string being tested, :meth:`~marbles.mixins.FileMixins.assertFileNameRegex` immediately tells you that the string being tested is a file name.

For example, let's say we've written a function that sorts a list of numbers (which we shouldn't have done because :func:`sorted` is included in the standard library). We can write a concise unit test for this function using mixin assertions about monotonicity

.. literalinclude:: examples/custom_assertions.py
   :emphasize-lines: 16-17

These custom assertions are provided via mixin classes so that they can use other assertions as building blocks. Using mixins, instead of straight inheritance, means that you can compose multiple mixins to create a test case with all the assertions that you need.

.. warning::

    :mod:`marbles.mixins` can be mixed into a :class:`unittest.TestCase`, a :class:`marbles.core.TestCase`, a :class:`marbles.core.AnnotatedTestCase`, or any other class that implements a :class:`unittest.TestCase` interface. To enforce this, mixins define `abstract methods <abc>`_. This means that, when mixing them into your test case, they must come `after` the class(es) that implement those methods instead of appearing first in the inheritance list like normal mixins.

    .. _abc: https://docs.python.org/3.5/library/abc.html#abc.abstractmethod

Writing your own mixins
^^^^^^^^^^^^^^^^^^^^^^^

You can write your own assertions and mix them in to your test cases, too. We recommend reading the :mod:`marbles.mixins` source code to see how to do this. Here is the :class:`~marbles.mixins.UniqueMixins` source as an example:

.. literalinclude:: ../marbles/mixins/marbles/mixins/mixins.py
   :lines: 348-425

If you write assertions that you think would be useful for others, we would love to see a `pull request`_ from you!

.. _pull request: https://github.com/twosigma/marbles/pulls

Logging
-------

You can configure :mod:`marbles.core` to log information about every assertion made during a test run as a JSON blob. This includes the test method name, the assertion, the result of the assertion, the arguments passed to the assertion, runtime variables, etc.

These logs can be transferred to another system for later analysis and reporting. For example, you could run :program:`logstash` after a test run to upload your logs to Elasticsearch, and then use Kibana to analyze them, maybe creating dashboards that show how many assertion failures you get over time, grouped by whether or not assertions are annotated.

See :mod:`marbles.core.log` for information on configuring the logger.
