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

from .marbles import (
    AnnotatedAssertionError,
    AnnotatedTestCase,
    AnnotationError
)
from .marbles import __doc__ as marbles_doc
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ['AnnotatedAssertionError', 'AnnotatedTestCase', 'AnnotationError']
__doc__ = marbles_doc
