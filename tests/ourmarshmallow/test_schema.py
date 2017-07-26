"""
Tests for our customized marshmallow Schema
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

import sqlalchemy as sa

from models import bases
import ourmarshmallow

warnings.simplefilter("error")  # Make All warnings errors while testing.


class DummyModel(bases.BaseModel):
    """ Copied from tests/models/test_base.py """
    email = sa.Column(sa.String(50), unique=True, nullable=False)


class DummySchema(ourmarshmallow.Schema):
    """ For testing schemas. """
    class Meta(object):  # pylint: disable=missing-docstring,too-few-public-methods
        model = DummyModel


def test_schema_session(dbsession):
    """
    Schemas should have a session on init.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    schema = DummySchema()
    assert schema.session == dbsession

def test_schema_type():
    """
    Schemas should have a session on init.
    """
    schema = DummySchema()
    assert schema.opts.type_ == 'dummy-model'

def test_schema_strict():
    """ Schema options should default to strict. """
    schema = DummySchema()
    assert schema.strict is True
