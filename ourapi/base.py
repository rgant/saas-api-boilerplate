"""
Base class for JSONAPI Resources in our api.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import flask.views


class BaseJsonApiResource(flask.views.MethodView):
    """ Root class for all JSONAPI Method View Classes. """
    pass
