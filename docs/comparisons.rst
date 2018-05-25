.. highlight:: python

Comparisons
===========

How does marbles compare to other Python testing tools?

For now, we focus on `pytest`_, which has the most in common with
marbles.

.. toctree::
   :maxdepth: 2


pytest
------

Marbles provides some functionality similar to `pytest`_:

* Full statement source code presentation
* Presentation of variables present in assertion statements

Marbles goes beyond pytest with:

* Note annotations
* Custom assertion mixins

Finally, marbles tests have the same structure as unittest tests,
which are more explicit than pytest tests, and therefore are easier to
learn and to reason about at failure time.

If you're familiar with pytest, you'll probably find that writing
marbles tests is more typing than you're used to, but we hope, no
matter which tool you know well, responding to a test failure will be
faster and easier with marbles. In short, pytest is write optimized,
while marbles is read optimized.

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

While pytest presents just the variables involved in the assertion
(and shows each sub-expression involved in the assertion), marbles
presents all public local variables in scope in the test method.

Marbles is a little more flexible here. While pytest has the ability
to expand complex expressions and present all of their constituent
names in the failure message, it doesn't present any other variables
leading up to the assertion, which may provide valuable context.

With marbles, you can get the same effect as pytest by simply
decomposing a complex assertion statement into its constituent parts,
and giving each of these parts a distinct local variable binding.

Consider the following pytest code::

    assert a * b < c * d

If this assertion fails, pytest will show you the values of the
expressions ``a * b`` and ``c * d``, as well as the individual values
of each variable ``a``, ``b``, ``c``, and ``d``.

In marbles, one could instead write this test as::

    lhs = a * b
    rhs = c * d
    self.assertLess(lhs, rhs)

Advantages of marbles
~~~~~~~~~~~~~~~~~~~~~

Note annotations
""""""""""""""""

Marbles gives the test author a place to :ref:`annotate assertion
statements <notes>` with information about not just a description of
what assertion failed, but also information about why that assertion
is important, or maybe what the test consumer should do to handle that
failure.

Custom assertion mixins
"""""""""""""""""""""""

Pytest relies on the bare ``assert`` keyword, and encourages use of it
directly. This puts the burden on the test consumer to understand the
author's intent. As a consumer, you need to parse the logic of the
assertion condition and read the rest of the test to understand what's
going on.

Marbles provides, through :mod:`marbles.mixins` classes, richly-named
assertion methods which convey the author's intent to the test
consumer. With marbles, the assertion name tells you explicitly what
is being checked.

Pure extension of unittest
""""""""""""""""""""""""""

While pytest gives you lots of power to be clever with fixtures when
writing tests, pytest failures are much more difficult to respond to.

It can be hard to piece together where fixtures come from, they might
not even be in the same file, or any that are imported. Even if you
can find the fixtures, it's unclear exactly what the control flow is.

Marbles works with unmodified :mod:`unittest` tests. We find unittest
tests have a clearer structure than pytest tests, especially those
with complicated fixtures.

With unittest, control flow is explicit, as long as you understand
basic Python semantics. There's no magic, it's just inheritance.

We have found that, at scale, unittest's boilerplate is a benefit
rather than a burden. It makes for tests that are more explicit about
what they're doing, and it encourages logical grouping of tests, both
of which reduce the test consumer's time to understand a failure.


.. _pytest: https://docs.pytest.org
