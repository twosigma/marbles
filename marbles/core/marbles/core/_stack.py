#
#  Copyright (c) 2018 Two Sigma Open Source, LLC
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#

import sys
import traceback


def get_stack_info():
    '''Capture locals, module name, filename, and line number from the
    stacktrace to provide the source of the assertion error and
    formatted note.
    '''
    stack = traceback.walk_stack(sys._getframe().f_back)

    # We want locals from the test definition (which always begins
    # with 'test_' in unittest), which will be at a different
    # level in the stack depending on how many tests are in each
    # test case, how many test cases there are, etc.

    # The branch where we exhaust this loop is not covered
    # because we always find a test.
    for frame, _ in stack:  # pragma: no branch
        code = frame.f_code
        if code.co_name.startswith('test_'):
            return (frame.f_locals.copy(), frame.f_globals['__name__'],
                    code.co_filename, frame.f_lineno)
