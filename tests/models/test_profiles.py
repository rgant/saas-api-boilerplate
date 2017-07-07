"""
Tests for the Profiles Model
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

import pytest

from models import profiles


warnings.simplefilter("error")  # Make All warnings errors while testing.

def test_email_validation():
    """ Must be a valid email address in model. """
    # Blanks are not allowed
    with pytest.raises(ValueError):
        profiles.Profiles(email='')

    with pytest.raises(ValueError):
        profiles.Profiles(email='bademail')

    # You can create model without an email
    inst = profiles.Profiles()

    # None is not a valid email value
    with pytest.raises(TypeError):
        inst.email = None

    # A valid email
    inst.email = 'f0ad@4f94.ab7d'
