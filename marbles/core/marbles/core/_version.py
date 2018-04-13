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

import os.path


with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as vfile:
    __version__ = vfile.read().strip()
