"""
Tests for the database module
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import os
import warnings

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.scoping import scoped_session

from models import db


warnings.simplefilter("error")  # Make All warnings errors while testing.

def test_env():
    """ Default environment should be dev. """
    assert not os.environ.get('ENV')  # First confirm that there isn't an ENV set.
    assert db.ENV == 'dev'

def test_connections():
    """ The three enviornments should each have different URLs. """
    assert 'dev' in db.CONNECTIONS
    assert 'stage' in db.CONNECTIONS
    assert 'prod' in db.CONNECTIONS
    assert db.CONNECTIONS['dev'] != db.CONNECTIONS['stage']
    assert db.CONNECTIONS['dev'] != db.CONNECTIONS['prod']
    assert db.CONNECTIONS['prod'] != db.CONNECTIONS['stage']

def test_engine():
    """ create and drop tables commands need ENGINE exposed """
    assert isinstance(db.ENGINE, Engine)

def test_factory():
    """ create and drop tables commands need ENGINE exposed """
    assert isinstance(db.FACTORY, scoped_session)
