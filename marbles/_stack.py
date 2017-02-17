import sys
import traceback


def get_stack_info():
    '''Capture locals, filename, and line number from the stacktrace to
    provide the source of the assertion error and formatted advice.
    '''
    tb = traceback.walk_stack(sys._getframe().f_back)
    stack = traceback.StackSummary.extract(tb, capture_locals=True)

    # We want locals from the test definition (which always begins
    # with 'test_' in unittest), which will be at a different
    # level in the stack depending on how many tests are in each
    # test case, how many test cases there are, etc.

    # The branch where we exhaust this loop is not covered
    # because we always find a test.
    for frame in stack:  # pragma: no branch
        if frame.name.startswith('test_'):
            return frame.locals.copy(), frame.filename, frame.lineno
