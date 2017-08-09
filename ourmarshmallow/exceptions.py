"""
Custom exceptions for our marshmallow
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

from marshmallow_jsonapi.exceptions import IncorrectTypeError


class MissingIdError(IncorrectTypeError):
    """
    Raised when a client fails to provide the id in a request. Special case so we can return the
    correct response code.
    """
    # Use same pointer as missing type check:
    # https://github.com/marshmallow-code/marshmallow-jsonapi/blob/17c6645845d8fe715c2de6d7f72ae908812660a9/marshmallow_jsonapi/schema.py#L138
    pointer = '/data'
    default_message = '`data` object must include `id` key.'


class MismatchIdError(IncorrectTypeError):
    """
    Raised when a client provides an id that doesn't match the request. Special case so we can
    return the correct response code.
    """
    pointer = '/data/id'
    default_message = 'Mismatched id. Expected "{expected}".'
