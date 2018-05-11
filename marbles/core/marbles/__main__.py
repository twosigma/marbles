#
#       Copyright (c) 2017 Two Sigma Investments, LP
#       All Rights Reserved
#
#       THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE OF
#       Two Sigma Investments, LP.
#
#       The copyright notice above does not evidence any
#       actual or intended publication of such source code.
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
    except ImportError:
        print('marbles.mixins not installed')
    else:
        print('marbles.mixins version: {}'.format(marbles.mixins.__version__))
    sys.exit(0)

__unittest = True

from marbles.core.main import main

main(module=None)
