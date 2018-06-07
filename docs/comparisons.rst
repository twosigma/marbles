.. highlight:: python

Comparisons
===========

How does marbles compare to other Python testing tools?

Marbles extends Python's built-in unittest library, so some of what
distinguishes marbles from other testing tools isn't about marbles as
much as it's about unittest. That being said, marbles extends unittest
---as opposed to another Python testing tool---for a reason.

In this section, we'll call out differentiating features of marbles
specifically, as well as differentiating features of unittest that
make unittest the right foundation for marbles.

For now, we focus on `pytest`_, which is widely used and whose failure
messages have the most in common with marbles failure messages.

.. toctree::
   :maxdepth: 2


pytest
------

As far as failure messages go, marbles has the most in common with
`pytest`_. However, because marbles is bulit on top of unittest,
writing marbles tests is pretty different than writing pytest tests.

Marbles is all about the test consumer, while pytest is all about the
test author. Pytest tries to make you more efficient while writing
tests and marbles tries to make you more efficient while reading,
reasoning about, and responding to test failures. You could say (and
we sometimes do) that pytest is write optimized and marbles is read
optimized.

If you're familiar with pytest, you'll probably find that writing
marbles tests is more typing than you're used to, but we hope, no
matter which tool you know well, responding to test failures will be
faster and easier with marbles. Marbles achieves this in a couple of
ways:

1. Marbles failures expose more information than pytest failures
2. Giving test authors the ability to curate what appears in the
   failure message encourages them to design their tests with the test
   consumer in mind
3. Unittest tests are more explicit than pytest tests, meaning it's
   easier to determine and reason about what tests are doing

Similarities
~~~~~~~~~~~~

Assertion Source
""""""""""""""""

Both marbles and pytest present the :ref:`source code <source>` of the
whole assertion statement that failed, which is more useful than a
typical Python traceback.

We believe both tools provide an equivalent benefit here.

Local Variables
"""""""""""""""

Both marbles and pytest present some of the local variables present at
the time an assertion in your test failed.

Pytest exposes only the variables that are involved in the assertion
(and shows each sub-expression involved in the assertion). Marbles
exposes any public variables that are in scope at the time the
assertion failed, whether or not they are direcly involved in the
assertion.

Advantages of marbles
~~~~~~~~~~~~~~~~~~~~~

Note annotations
""""""""""""""""

Marbles allows test authors to :ref:`annotate assertion statements
<notes>` with additional information about the test and the author's
intent that will help the test consumer put the failed assertion in
context.

Explicit assertion names
""""""""""""""""""""""""

Pytest relies on the bare ``assert`` keyword, and encourages use of it
directly. This puts the burden on the test consumer to derive the
author's intent. As a consumer, you need to parse the logic of the
assertion condition and read the rest of the test to understand what's
going on.

Instead of the ``assert`` keyword, marbles tests use the assertion
methods provided by unittest. Unittest's assertions methods have
semantically-rich names that help convey the author's intent to the
test consumer in almost-plain English. We believe that, because the
assertion statement that failed will be exposed in the failure message,
is is worthwhile to write assertion statements that are as descriptive
and easy to understand as possible.

Furthermore, relying on the ``assert`` keyword makes it
difficult to ensure that similar expectations are being asserted in
comparable ways. Having a standard set of specific assertion methods
helps ensure that similar assertions are made in the same way. For
example, every test that uses the :meth:`~unittest.TestCase.assertRegex`
assertion will test for a regex match in the same way.

The :mod:`marbles.mixins` package provides even more and
semantically-richer assertion methods on top of the standard set of
unittest assertions. You are also free to write your own assertion
methods. The :mod:`marbles.mixins` provide a good template for building
out a set of custom assertions that may be unique to your business or
use case.

Local variable control
""""""""""""""""""""""

Both marbles and pytest expose some of the test's local "state". Pytest
failure messages include any variables included in the assertion
statement, and will expand any complex expressions that are present in
the assertion. Any variables that are not used in the assertion will
not be displayed, meaning we don't see any variables that may have been
defined leading up to the assertion.

For example, consider the following pytest code::

    assert a * b < c * d

If this assertion fails, pytest will show you the values of the
expressions ``a * b`` and ``c * d``, as well as the individual values
of each variable ``a``, ``b``, ``c``, and ``d``.

Marbles will display any public local variables defined within the test
at the time it failed, regardless of whether or not they were used
in the failing assertion.

Consider the same example as above written in marbles::

    self.assertLess(a * b, c * d)

If this assertion fails, marbles will show you the values of ``a``,
``b``, ``c``, and ``d``, but not the values of the expressions
``a * b`` or ``c * d``. If it's valuable for the test consumer to also
see the values of these expressions, we can achieve that by assigning
them to variables::

    lhs = a * b
    rhs = c * d
    self.assertLess(lhs, rhs)

If we want to exclude any local variables from the failure message,
all we need to do is give them "internal" or "private" names, i.e.,
prefix the variable names with an underscore.

This gives the test author natural---and pretty neutral---control over
what local variables will be displayed in the failure message. In
pytest, in order for locals to appear in the failure message they need
to be used in the assertion. In marbles, they need only be public.

Pure extension of unittest
""""""""""""""""""""""""""

While pytest gives you lots of power to be clever with fixtures when
writing tests, this is often at the expense of being able to easily
understand what any given test is doing when you're trying to debug a
failure.

It can be hard to piece together where fixtures come from: they might
not even be in the same file, or any that are imported. Even if you
can find the fixtures, it's unclear exactly what the control flow is.
This gets particularly complicated if the author used
:file:`conftest.py` anywhere in the project.

Marbles works with unmodified :mod:`unittest` tests. We find unittest
tests have a clearer structure than pytest tests, especially those
with complicated fixtures. With unittest, control flow is explicit, as
long as you understand basic Python semantics. There's no magic, it's
just inheritance.

We have found that, at scale, unittest's boilerplate is a benefit
rather than a burden. It makes for tests that are more explicit about
what they're doing, and it encourages logical grouping of tests, both
of which reduce the test consumer's time to understand a failure.


.. _pytest: https://docs.pytest.org
