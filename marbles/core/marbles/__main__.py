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

# This file is mostly copied from unittest.__main__, because something
# which cleanly imports it instead of duplicating its functionality
# doesn't really work.

'''Main entry point'''

import sys
# I don't think it's possible to cover the fact that we never skip
# this branch.
if sys.argv[0].endswith('__main__.py'):  # pragma: no branch
    import os.path
    # We change sys.argv[0] to make help message more useful
    # use executable without path, unquoted
    # (it's just a hint anyway)
    # (if you have spaces in your executable you get what you deserve!)
    executable = os.path.basename(sys.executable)
    sys.argv[0] = executable + ' -m marbles'
    del os

if len(sys.argv) > 1 and sys.argv[1] == '--version':
    import marbles.core
    print('marbles.core version: {}'.format(marbles.core.__version__))
    try:
        import marbles.mixins
    except ImportError:  # pragma: no cover
        # Our tests run with both subpackages installed, it's probably
        # not worth the effort it would take to cover this branch.
        print('marbles.mixins not installed')
    else:
        print('marbles.mixins version: {}'.format(marbles.mixins.__version__))
    sys.exit(0)

__unittest = True

from marbles.core.main import main  # noqa: E402

main(module=None)
