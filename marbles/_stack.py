import sys
import traceback


def get_stack_info():
    '''Capture locals, module name, filename, and line number from the
    stacktrace to provide the source of the assertion error and
    formatted advice.
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
