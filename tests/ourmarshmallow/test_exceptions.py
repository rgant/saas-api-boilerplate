"""
Tests for our marshmallow exceptions
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

import ourmarshmallow.exceptions


warnings.simplefilter("error")  # Make All warnings errors while testing.

def test_missing_id_error():
    """ Confirm defaults for MissingIdError. """
    exc = ourmarshmallow.exceptions.MissingIdError()
    exc.messages == {'errors': [{'detail': '`data` object must include `id` key.',
                                 'source': {'pointer': '/data'}}]}

def test_mismatch_id_error():
    """ Confirm defaults for MismatchIdError. """
    exc = ourmarshmallow.exceptions.MismatchIdError(actual='999', expected='100')
    exc.messages == {'errors': [{'detail': 'Mismatched id. Expected "100".',
                                 'source': {'pointer': '/data/id'}}]}
