"""
Tests for the API basic structure.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings


warnings.simplefilter("error")  # Make All warnings errors while testing.

def test_health_check(appclient):
    """ API nominal health check should respond "True" if the API is running. """
    response = appclient.get('/health')
    assert response.status_code == 200
    assert response.data == b'True'
