# marbles

`marbles` is a small `unittest` extension by [Jane Adams](mailto:jane@twosigma.com) and [Leif Walsh](mailto:leif@twosigma.com) that allows test authors to provide additional information to test consumers on test failure.

## Background

Two Sigma needs to make assertions about different resources, e.g., directories, files, pandas DataFrames, etc. These are generally referred to as "sanity checks". Python's builtin `unittest` module is a natural framework for expressing these assertions. That being said, testing functionality (which is what `unittest` is designed to do) is different than testing a resource. If an assertion about a piece of functionality fails, you go inspect the code that defines that functionality. If an assertion about a resource fails, it is not as obvious what you should do.

Generally, the data product owner has the most insight into 1) what sanity checks should be written, and 2) what needs to happen if/when any of those sanity checks fail. Building that insight into the definition of the sanity checks themselves, and exposing that insight on test failure, will mean that the data product owner doesn't have to maintain that information in their head or in disconnected documentation (which is always at risk of becoming outdated). It also means that other consumers of failed test output will be able to effectively diagnose and even resolve errors if the data product owner is not available.

When writing assertions about resources using `marbles`, the test author provides this insight in the form of advice, namely, "if this test fails this is what you should do". This advice can be as general or as specific as needed. It can contain commands to run, people to email, anything that can be expressed in a string.

# Getting Started

## Installation

You can either clone this repostory and run the setup script, or install `marbles` from GitLab using pip. It is highly recommended that you only install `marbles` within a conda environment.

```bash
(env) $ git clone git@gitlab.twosigma.com/jane/marbles.git
(env) $ cd marbles && python setup.py install
```

```bash
(env) $ pip install -U git+ssh://git@gitlab.twosigma.com/jane/marbles.git@master
```

## Tests

The `marbles` test suite is written in the [unittest](https://docs.python.org/3.5/library/unittest.html) framework. To run the tests, execute the following from the root of the cloned repository

```bash
/path/to/marbles $ python -m unittest tests
```

# Overview

Writing `marbles` test cases is, intentionally, very similar to writing `unittest` TestCases. The main difference is that, in a `marbles.AnnotatedTestCase`, the `assert*` methods, in addition to accepting an optional final string parameter ``msg``, expect a keyword parameter ``advice``, which should describe what steps should be taken when the test fails.

On test failure, the `msg` and `advice` strings are formatted with the local variables defined within the test itself, which is crucial information when testing resources, especially if those resources can change. The `msg`, `advice`, and locals allow the test consumer to reconstruct, at the point of test failure, what the expectation was, what the resource actually was, and what to do about it.

## Example

Below is an example test file that uses the `marbles` `AnnotatedTestCase`. You'll notice that there is one succeeding and one failing test.

```python
import os
import re
import unittest

from marbles import AnnotatedTestCase


filename = 'file_2016_01_01.py'


class FilenameTestCase(AnnotatedTestCase):
    '''FilenameTestCase makes assertions about a filename.'''

    def setUp(self):
        self.filename = filename

    def tearDown(self):
        delattr(self, 'filename')

    def test_filetype(self):
        '''Verifies file type.'''
        expected = '.py'
        actual = os.path.splitext(self.filename)[1]

        advice = ('Tell Jane Doe that we expected a {expected} file but '
                  'received a {actual} file. If we should expect {expected} '
                  'files moving forward, please update this test.')

        self.assertEqual(expected, actual, advice=advice)

    def test_filename_pattern(self):
        '''Verifies filename pattern.'''
        expected = '^file_[0-9]{8}$'
        actual = os.path.splitext(self.filename)[0]

        advice = ('Determine if this is a one-off error or if the file naming '
                  'pattern has changed to {actual}. If the file naming '
                  'pattern has changed, please update this test.')

        self.assertRegex(actual, expected, advice=advice)


if __name__ == '__main__':
    unittest.main()
```

The output of running this test case

```bash
(env) /path/to/tests $ python -m unittest example
F.
======================================================================
FAIL: test_filename_pattern (examples.filename.FilenameTestCase)
Verifies filename pattern.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/jane/Development/marbles/examples/filename.py", line 40, in test_filename_pattern
    self.assertRegex(actual, expected, advice=advice)
  File "/home/jane/Development/marbles/marbles/marbles.py", line 416, in wrapper
    return attr(*args, msg=annotation, **kwargs)
marbles.marbles.AnnotatedAssertionError: Regex didn't match: '^file_[0-9]{8}$' not found in 'file_2016_01_01'

Source:
     39
 >   40 self.assertRegex(actual, expected, advice=advice)
     41
Locals:
	expected='^file_[0-9]{8}$'
	actual='file_2016_01_01'
Advice:
	Determine if this is a one-off error or if the file naming pattern has
	changed to 'file_2016_01_01'. If the file naming pattern has changed,
	please update this test.


----------------------------------------------------------------------
Ran 2 tests in 0.003s

FAILED (failures=1)
```

## Controlling Test Output

Variables can be excluded from the "Locals" section of the test output by making them internal or name-mangled (prepending the variable name with one or two underscores). This can be useful for hiding especially large variables (e.g., DataFrames) that are needed in the test but aren't needed and/or are overwhelming in the test output. Internal and name-mangled variables will still be formatted into message and advice strings if there are matching directives for them, but if you're internalizing/name-mangling a variable because it's value is large you probably don't want to include it in your annotations.

```python
def test_dataframe(self):
    '''Is something about a DataFrame true?'''
    foo = 'bar'
    _ignoreme = pd.DataFrame()

    message = 'some message'
    advice = 'some advice'

    self.assertSomethingAbout(_ignoreme, (message, advice))
```

When this test fails, you'll see the following output. Notice that `_ignoreme` has been excluded from the "Locals" section.

```bash
======================================================================
FAIL: test_dataframe (__main__.DataFrameTestCase)
Is something about a DataFrame true?
----------------------------------------------------------------------
Traceback (most recent call last):
  File "somefile.py", line 48, in test_dataframe
    self.assertSomethingAbout(_ignoreme, (message, advice))
marbles.marbles.AnnotatedAssertionError
some message

Source:
     47
 >   48 self.assertSomethingAbout(_ignoreme, (message, advice))
     49
Locals:
        foo='bar'
Advice:
        some advice
```
## Future Work

`marbles` is the first step toward extending `unittest` to support assertions we may want to express about resources. Future extensions will most likely focus on:
1. enabling test authors to pass trivially different/dynamic resources to the same test cases, and
2. enabling better programmatic interaction with test failures to make it easier to aggregate them into a single report covering multiple resources
