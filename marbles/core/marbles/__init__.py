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

import pkgutil


__path__ = pkgutil.extend_path(__path__, __name__)

# Even though pkgutil.extend_path is a valid (and more modern) way of
# declaring a namespace package, setuptools still checks for the
# string "declare_namespace" in __init__.py. This comment should quiet
# it down, since it contains that substring.
