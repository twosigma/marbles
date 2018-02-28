============
Introduction
============

What is marbles?
================

marbles is a :py:class:`unittest` extension that allows test authors to write richer tests and expose more actionable information on test failure.

When writing marbles assertions, the test author provides actionable information about what to do when the test fails in the form of `advice`_. On test failure, this advice is provided back to the test consumer, along with `locals`_ defined within the test itself. These advice annotations leverage test locals using format strings (see `leveraging locals`_), making it possible to write a single test against multiple resources and/or parametrizations while still providing specific, actionable advice.

marbles also provides a set of semantically rich assertions via `mixins`_ that go beyond the generic predicates available in :py:mod:`unittest`. These richer assertions provide the test consumer with more context about the resource and predicate being tested. For example, while :py:meth:`~unittest.TestCase.assertRegex` doesn't tell the test consumer anything about the string being tested, :meth:`~marbles.mixins.FileMixins.assertFileNameRegex` immediately tells the test consumer that the string being tested is a filename.

Example
=======

The AnnotatedTestCase
---------------------

:class:`marbles.AnnotatedTestCase` s are almost exactly like :py:class:`unittest.TestCase` s. The main difference is that ``assert`` methods on a :class:`marbles.AnnotatedTestCase` take an additional parameter, ``advice``.

.. _sla:

.. literalinclude:: ../examples/sla.py
   :emphasize-lines: 33,40

Output
------

Similarly, marbles output is very similar to :py:mod:`unittest` output, but includes three additional sections:

1. Source: the source line of code containing the assertion that failed
2. `Locals`_: any public variables defined within the test itself
3. `Advice`_: additional information provided by the test author

This is the output of the example :ref:`SLATestCase <sla>` above:

.. code-block:: bash
   :emphasize-lines: 12,16,18,33,37,40

    FF
    ======================================================================
    FAIL: test_for_pii (__main__.SLATestCase)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "examples/sla.py", line 40, in test_for_pii
        self.assertNotRegex(self.data, ssn_regex, advice=advice)
      File "/home/jane/Development/marbles/marbles/marbles.py", line 431, in wrapper
        return attr(*args, msg=annotation, **kwargs)
    marbles.marbles.AnnotatedAssertionError: Regex matched: '123-45-6789' matches '\\d{3}-?\\d{2}-?\\d{4}' in '12345,2017-01-01,iPhone 7,649.00,123-45-6789'

    Source:
         39 ssn_regex = '\d{3}-?\d{2}-?\d{4}'
     >   40 self.assertNotRegex(self.data, ssn_regex, advice=advice)
         41 
    Locals:
            ssn_regex=\d{3}-?\d{2}-?\d{4}
    Advice:
            data.csv appears to contain SSN(s). Please report this incident to
            legal and compliance.
        

    ======================================================================
    FAIL: test_on_time_delivery (__main__.SLATestCase)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "examples/sla.py", line 33, in test_on_time_delivery
        self.assertGreaterEqual(datadate, on_time_delivery, advice=advice)
      File "/home/jane/Development/marbles/marbles/marbles.py", line 431, in wrapper
        return attr(*args, msg=annotation, **kwargs)
    marbles.marbles.AnnotatedAssertionError: datetime.date(2017, 1, 1) not greater than or equal to datetime.date(2017, 2, 28)

    Source:
         32 
     >   33 self.assertGreaterEqual(datadate, on_time_delivery, advice=advice)
         34 
    Locals:
            on_time_delivery=2017-02-28
            datadate=2017-01-01
    Advice:
            The data in data.csv are out of date. If this is a recurring issue,
            contact the data provider to negotiate a reimbursement or to re-
            negotiate the terms of the contract.
        

    ----------------------------------------------------------------------
    Ran 2 tests in 0.009s

    FAILED (failures=2)


=====================
How to win at marbles
=====================

marbles can be used anywhere :py:mod:`unittest` is used. Like :py:mod:`unittest`, and unit testing in general, there are places where marbles works well and places where it doesn't work well. marbles works well when:

1. there's a concrete expectation that you can test for, and
2. it's not obvious what needs to happen when expectations are violated.

If there's no "correct answer" that you know ahead of time, unit testing (using marbles or :py:mod:`unittest`) might not be the right approach. (This is why predictive models, for example, aren't unit tested.) If there is a correct answer that you can test for but it's obvious what needs to happen when you don't get that answer, marbles might be overkill.

    One scenario in which it might not be obvious what needs to happen when a test fails is if it can fail in the same way for different, well-known reasons. In this scenario, the test consumer first needs to figure out which failure condition(s) apply and then figure out how to respond. This is what `Advice`_ annotations are for, but the "well-known" part is important: if the failure conditions aren't well-known, what advice could you give the test consumer to help them figure out what happened?

Ultimately, how you leverage `Locals`_ and `Advice`_ depends on what you're using marbles to test. Below are recommendations for how to fully leverage marbles when you're testing data specifically, but many of these recommendations could apply to other testing scenarios as well.

Unit Testing Data
=================

marbles was originally built for unit testing data. In the same way that we need to make assertions about how code functions, we need to make assertions about data. These can range from asserting that SLAs are being met and that the data are well-formed to asserting that the fidelity of the signal in a dataset hasn't been lost.

:py:mod:`unittest` is a natural framework for expressing these assertions, which is why :class:`marbles.AnnotatedTestCase` so closely resembles :py:class:`unittest.TestCase`. But, making assertions about data is different than making assertions about code in two main ways:

    First, it's not always obvious how data should function, i.e., what data failure even looks like.

    Second, when a unit test about a function fails, you go look at the source code for the function to figure out what went wrong. (It can get more complex than that, but the point is that generally you know where to start.) When a unit test about data fails, it's not as obvious what you're supposed to do. A reasonble place to start might be looking at the data, but that only makes sense for some of the things we might be testing for. What if the failure is that you didn't even get the data?

This is where marbles comes in:

1. **Expose relevant, actionable information when tests fail:** when writing assertions using marbles, the test author provides information about what to do if the test fails in the form of `Advice`_. On test failure, this advice is provided to the test consumer along with the test `Locals`_.

2. **Improve and codify knowledge about when and how data will fail:** marbles provides a set of custom, :mod:`unittest`-style assertions for common data failures (see `Mixins`_ for more information). These custom assertions are intended to perturb the test author's knowledge of a dataset and help them better "cover their bases" with tests.

By requiring that test authors better understand and codify the ways in which data can fail, marbles helps catch more data failures; by requiring test authors to provide instructions on how to mitigate those failures, marbles helps more people productively respond to those failures.

Locals
======

Local variables defined within the test are included in the "Locals" section of the test output. This allows the test consumer to reconstruct the state at the time the test failed.

Test authors are encouraged to "curate" their locals to include information that will help the test consumer quickly diagnose and resolve failures, keeping in mind that including too few locals can be as detrimental as including too many.

Excluding Locals
----------------

Not all local variables will be relevant to the test consumer, and including them in the "Locals" section would be more distracting than helpful. Local variables can be excluded from the "Locals" section by making them internal or name-mangled (prepending them with one or two underscores).

.. note::
   
   The local variables ``self`` and ``advice`` are automatically excluded from the "Locals" section.

Locals-Only Locals
------------------

Some information that would be relevant to the test consumer may not be needed by your test. We recommend creating local variables for these anyway.

.. note::

   Python linters like `flake8`_ will complain about variables that are assigned but never used, but most linters provide ways of ignoring specific lines.

   .. _flake8: http://flake8.pycqa.org/en/latest/

Advice
======

Advice annotations are intended to tell the test consumer what to do when the test fails. In conjunction with the `Locals`_, they should provide the test consumer with enough context and information to mitigate any failures.

.. note::

   We recommend that test authors bind advice annotations to a variable named ``advice``, or pass them to assertions directly, so that they're not repeated in the "Locals" section. Otherwise, test authors will need to manually exclude them from the "Locals" section. See `Excluding Locals`_ for more information.

Good Advice
-----------

Advice annotations can be as general or as specific as needed, but the best annotations contain the following:

1. condition(s) under which the test will or could fail
2. instructions for determining which failure condition(s) hold
3. instructions for mitigating the applicable failure condition(s)

What does good advice look like? Let's expand on the advice in the SLA example above:

.. code-block:: python

    class SLATestCase(AnnotatedTestCase):
        '''SLATestCase ensures that SLAs are being met.'''

        # Class attributes are helpful for storing information that
        # is needed in more than one advice annotation and that won't
        # change between tests
        data_engineer = 'Jane Doe'
        lc_contact = 'lc@company.com'
        vendor_id = 'V100'

        ...

        def test_for_pii(self):
            advice = '''This test will fail if

        1) the vendor provided data containing SSNs, and

        2) our internal SSN filtering is unsuccessful.

    The vendor should not provide data containing PII, and this incident
    should be reported to Legal & Compliance ({self.lc_contact})
    immediately. In your report, please include the vendor ID,
    {self.vendor_id}, and the name of the file containing the PII,
    {self.filename}.

    Our internal PII filtering algorithm is maintained here: {_ssn_filter}.
    Create a new issue on that project to report this bug and assign it to
    {self.data_engineer}, but *do not* include any PII in the issue.
    '''

            _ssn_filter = 'http://gitlab.com/group/repo'  # noqa: F481

            ssn_regex = '\d{3}-?\d{2}-?\d{4}'
            self.assertNotRegex(self.data, ssn_regex, advice=advice)

This will give the following output on failure:

.. code-block:: bash

    F
    ======================================================================
    FAIL: test_for_pii (__main__.SLATestCase)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "examples/sla.py", line 61, in test_for_pii
        self.assertNotRegex(self.data, ssn_regex, advice=advice)
      File "/home/jane/Development/marbles/marbles/marbles.py", line 482, in wrapper
        return attr(*args, msg=annotation, **kwargs)
    marbles.marbles.AnnotatedAssertionError: Regex matched: '123-45-6789' matches '\\d{3}-?\\d{2}-?\\d{4}' in '12345,2017-01-01,iPhone 7,649.00,123-45-6789'

    Source:
         60 ssn_regex = '\d{3}-?\d{2}-?\d{4}'
     >   61 self.assertNotRegex(self.data, ssn_regex, advice=advice)
         62
    Locals:
            ssn_regex=\d{3}-?\d{2}-?\d{4}
    Advice:
            This test will fail if

                1) the vendor provided data containing SSNs, and

                2) our internal SSN filtering is unsuccessful.

            The vendor should not provide data containing PII, and this incident
            should be reported to Legal & Compliance (lc@company.com) immediately.
            In your report, please include the vendor ID, V100, and the name of the
            file containing the PII, data.csv.

            Our internal PII filtering algorithm is maintained here:
            'http://gitlab.com/group/repo'. Create a new issue on that project to
            report this bug and assign it to Jane Doe, but *do not* include any PII
            in the issue.

This advice provides two specific actions that test consumer needs to take and makes email addresses, links, etc. readily available. Instead of just "please report this to Legal & Compliance", an actual email address is provided as well as the information that needs to be included in the report. Instead of just "please report this bug", a URL to the project repository is provided, as well as the name of the person to assign the issue to.

Advice Writer's Block
^^^^^^^^^^^^^^^^^^^^^

If you're struggling to come up with the three pieces of information above, it may indicate that you don't fully understand the failure condition(s) and/or the significance of failure.

If you don't know how or why a test will or could fail, revisit the failures that inspired you to write the test in the first place. Re-read emails, bug reports, etc. to see if you can determine what caused the failure you're now testing for and include that in the advice.

.. note::

   Some failures are just flukes that can occur in any dataset, e.g., getting a dataset with dates in the future or dates from the year A.D. 14. If you've seen this enough times, you learn to test for it, and this is a good use case for a marbles test even if you can't write down why it might fail for a new dataset at first.

If you don't know what should happen when a test fails, reach out to the people that use the thing you're testing. They should be able to tell you what needs to happen when a particular test fails.

Sometimes, while writing advice, you'll realize that nothing really needs to happen when a test fails. That's a good time to consider getting rid of that test.

Bad Advice
----------

Advice annotations shouldn't contain the following:

1. restatement(s) of the failure
2. assumptions about development environments

What does bad advice look like? Let's use a `file`_ example. This example uses a `marbles mixin <Mixins>`_, which we'll get to later.

.. code-block:: python

    import os

    import marbles
    from marlbes import mixins


    class FileTestCase(marbles.AnnotatedTestCase, mixins.FileMixins):

        ...

        def test_that_file_exists(self):
            advice = '''{self.fname} doesn't exist, which is wild because
    the string you're reading right now is written in that file. List the
    contents of the data directory {_data_dir} to see if any other files
    are missing.'''

            _data_dir = os.getcwd()
            self.assertFileExists(self.fname, advice=advice)

This will give the following output on failure:

.. code-block:: bash
   :emphasize-lines: 23, 25

    F
    ======================================================================
    FAIL: test_that_file_exists (__main__.FileTestCase)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "examples/file.py", line 23, in test_that_file_exists
        self.assertFileNotExists(self.fname, advice=advice)
      File "/home/jane/Development/marbles/marbles/marbles.py", line 431, in wrapper
        return attr(*args, msg=annotation, **kwargs)
      File "/home/jane/Development/marbles/marbles/mixins.py", line 519, in assertFileNotExists
        self.fail(self._formatMessage(msg, standardMsg))
      File "/home/jane/Development/marbles/marbles/marbles.py", line 460, in wrapper
        return attr(*args, msg=msg, **kwargs)
    marbles.marbles.AnnotatedAssertionError: examples/file.py does not exist

    Source:
         22 _data_dir = os.getcwd()
     >   23 self.assertFileExists(self.fname, advice=advice)
         24 
    Locals:

    Advice:
            examples/file.py doesn't exist, which is wild because the string you're
            reading right now is written in that file. List the contents of the
            data directory /home/user/data/ to see if any other files
            are missing.

Firstly, the beginning of the advice just restates the standard message and so is a waste of the test consumer's time. Also, the recommended action contains the path to the data directory `on the test author's machine`; the relevant directory might be somewhere completely different on the test consumer's machine, so this information won't help them find the missing file.


Dynamic Advice
--------------

Test authors may want to provide different advice in different scenarios.

Leveraging Locals
^^^^^^^^^^^^^^^^^

On test failure, local variables are formatted into advice annotations (if there are matching field names for them), allowing the test author to write more dynamic and detailed advice.

One common use case for leveraging locals in advice is for `Parametrized Tests`_. Without leveraging locals in advice, the test author is only able to provide generic advice that applies to all parameter combinations, or unnecessarily verbose advice that captures all parameter combinations, forcing the test consumer to look at the locals to figure out what to pay attention to.

By leveraging locals in advice annotations, the test author can provide specific (and hopefully actionable) information for each parameter combination.

Criticality
^^^^^^^^^^^

Test authors may need to adjust advice based on the severity or criticality of the result. Let's say that, based on your experience with a dataset, you determine that month-to-month changes usually don't exceed 10X. You would first write a test that asserts that month-to-month changes are within 10X of each other.

But what if you need to respond differently when a change is 20X the previous month and differently still when a change is 100X the previous month? To achieve this, test authors can write multiple different assertions, each of which accepts a different advice annotation. In the example above, the test author would write three different assertions:

1. assert that change is within 100X
2. assert that change is within 20X
3. assert that change is within 10X

These assertions would accept different advice annotations, each of which would contain different instructions:

1. stop any and all processes using these data
2. file a JIRA with the data provider
3. monitor this test for the next month

In this example, we'd want to test for the most severe failure first; 2 and 3 would also fail if 1 fails, but the correct action to take is the action specified in the advice provided to the 1st assertion, so that is the advice that we want the test consumer to see.


.. literalinclude:: ../examples/severity.py


If you want the test consumer to have the advice for each severity level (i.e., you've written advice that builds naturally on itself with severity), you could loop through the severity assertions using :ref:`subtests <python:subtests>` instead of a ``for`` loop.

Mixins
======

The :mod:`marbles.mixins` module provides custom :py:mod:`unittest`-style assertions for common data failures. For the most part, marbles assertions trivially wrap :py:mod:`unittest` assertions. For example, a call to :meth:`~marbles.mixins.FileMixins.assertFileNameRegex` will simply forward the arguments to :py:meth:`~unittest.TestCase.assertRegex`.

These assertions, because they're more detailed, can provide the test consumer with additional information about the expected relationship between the thing being tested and what it's being tested against. :py:meth:`~unittest.TestCase.assertRegex` doesn't tell the test consumer anything about the string being tested; :meth:`~marbles.mixins.FileMixins.assertFileNameRegex` immediately tells the test consumer that the string being tested is a filename.

In addition, providing these more specific assertions can alert test authors of what they `should` be testing for when they're testing data. For instance, having a :meth:`~marbles.mixins.DateTimeMixins.assertDateTimesPast` assertion can inspire a eureka! moment for a test author that, yes, they expect all dates to be in the past.

.. warning::

    :mod:`marbles.mixins` can be mixed into a :py:class:`unittest.TestCase` or a :class:`marbles.AnnotatedTestCase`, or any other class that implements a :py:class:`unittest.TestCase` interface. To enforce this, mixins define `abstract methods <abc>`_. This means that, when mixing them into your test case, they must come `after` the class(es) that implement those methods instead of appearing first in the inheritance list like normal mixins.

    .. _abc: https://docs.python.org/3.5/library/abc.html#abc.abstractmethod

Example
-------

:mod:`marbles.mixins` assertions are provided via mixins so that they can use other assertions as building blocks. Using mixins, instead of straight inheritance, means that test authors can compose multiple mixins to create test cases that have all the assertions they need. The example below uses both :class:`~marbles.mixins.FileMixins` and :class:`~marbles.mixins.BetweenMixins`.

.. _file:

.. literalinclude:: ../examples/file.py
   :emphasize-lines: 8,9,10

Available Mixins
----------------

These are the currently available mixins, and we plan to add many more.

* :class:`~marbles.mixins.BetweenMixins`
* :class:`~marbles.mixins.MonotonicMixins`
* :class:`~marbles.mixins.UniqueMixins`
* :class:`~marbles.mixins.CategoricalMixins`
* :class:`~marbles.mixins.DateTimeMixins`
* :class:`~marbles.mixins.DataFrameMixins`
* :class:`~marbles.mixins.PanelMixins`

Parametrized Tests
==================

See the foundation documentation on `Parametrized Test Cases`_ for recommended ways of loading and parametrizing resources for testing.

.. _parametrized test cases: http://tsmerejenkins.app.twosigma.com:8080/job/Modeling_Compute_and_Analysis/job/py3/job/foundation/PYTHON_VERSION=3.5,agents=tsmoto/Sphinx_Docs/
