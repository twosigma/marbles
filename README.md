# marbles

`marbles` is a small `unittest` extension by [Jane Adams](mailto:jane.adams@twosigma.com) and [Leif Walsh](leif.walsh@twosigma.com) that allows test authors to provide additional information to test consumers on test failure.

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
(env) $ pip install -U git+ssh://gitlab.twosigma.com/jane/marbles.git@master
```

## Tests

The `marbles` test suite is written in the [unittest](https://docs.python.org/3.5/library/unittest.html) framework. To run the tests, execute the following from the root of the cloned repository

```bash
/path/to/marbles $ python -m unittest tests
```

# Overview

Writing `marbles` test cases is, intentionally, very similar to writing `unittest` TestCases. The main difference is that, in a `marbles.AnnotatedTestCase`, the `assert*` methods, rather than accepting an option final string parameter `msg`, require a tuple or a dictionary containing a message and some advice for the test consumer.

On test failure, the message and advice strings are formatted with the local variables defined within the test itself, which is crucial information when testing resources, especially if those resources can change. The message, advice, and locals allow the test consumer to reconstruct, at the point of test failure, what the expectation was, what the resource actually was, and what to do about it.

## Example

Below is an example test file that uses the `marbles` AnnotatedTestCase. You'll notice that there is one succeeding and one failing test.

```python
import os
import re
import unittest

from marbles import AnnotatedTestCase

filename = 'file_2016_01_01.py'

class FilenameTestCase(AnnotatedTestCase):
    '''FilenameTestCase makes assertions about a filename.'''
    
    def setup(self):
        self.filename = filename

    def teardown(self):
        delattr(self, 'filename')

    def test_filetype(self):
        '''verifies file type.'''
        expected = '.py'
        actual = os.path.splitext(self.filename)[1]

        message = 'expected a {expected} file but received a {actual} file.'
        advice = 'contact the ingestion owner: jane doe'

        self.assertequal(expected, actual, (message, advice))

    def test_filename_pattern(self):
        '''verifies filename pattern.'''
        expected = '^file_[0-9]{8}$'
        actual = os.path.splitext(self.filename)[0]

        message = 'filename {actual} does not match the pattern {expected}.'
        advice = ('determine if this is a one-off error or if the file naming '
                  'pattern has changed. if the file naming pattern has changed, '
                  'consider updating this test.')

        self.assertisnotnone(re.search(expected, actual), (message, advice))


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
  File "/home/jane/Development/marbles/examples/filename.py", line 38, in test_filename_pattern
    self.assertIsNotNone(re.search(expected, actual), (message, advice))
marbles.marbles.AnnotatedAssertionError: unexpectedly None
Filename 'file_2016_01_01' does not match the pattern '^file_[0-9]{8}$'.

Source:
     37
 >   38 self.assertIsNotNone(re.search(expected, actual), (message, advice))
     39
Locals:
        actual='file_2016_01_01'
        expected='^file_[0-9]{8}$'
Advice:
        Determine if this is a one-off error or if the file naming
        pattern has changed. If the file naming pattern has changed,
        consider updating this test.


----------------------------------------------------------------------
Ran 2 tests in 0.004s

FAILED (failures=1)
```

## Future Work

`marbles` is the first step toward extending `unittest` to support assertions we may want to express about resources. Future extensions will most likely focus on enabling test authors to pass trivially different/dynamic resources to the same test cases.
