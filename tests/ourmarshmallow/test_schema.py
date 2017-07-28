"""
Tests for our customized marshmallow Schema
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import datetime
import warnings

import sqlalchemy as sa

from models import bases
import ourmarshmallow

warnings.simplefilter("error")  # Make All warnings errors while testing.


class FakeModel(bases.BaseModel):
    """ Copied from tests/models/test_base.py """
    email = sa.Column(sa.String(50), unique=True, nullable=False)


class FakeSchema(ourmarshmallow.Schema):
    """ For testing schemas. """
    class Meta(object):  # pylint: disable=missing-docstring,too-few-public-methods
        model = FakeModel


def test_schema_session(dbsession):
    """
    Schemas should have a session on init.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    schema = FakeSchema()
    assert schema.session == dbsession

def test_schema_type():
    """
    Schemas should type_ set to kebab-case of model.__name__.
    """
    schema = FakeSchema()
    assert schema.opts.type_ == 'fake-model'

def test_schema_strict():
    """ Schema options should default to strict. """
    schema = FakeSchema()
    assert schema.strict is True

def test_schema_dump():
    """ Should return JSONAPI envelope for FakeModel. """
    now = datetime.datetime(2017, 7, 27, 18, 6, 3)
    the_model = FakeModel(id='45071', email='8cf0@4fc3.a865', modified_at=now)
    the_schema = FakeSchema()
    data = the_schema.dump(the_model).data
    expected = {'data': {'type': 'fake-model', 'id': 45071,
                         'attributes': {'email': '8cf0@4fc3.a865'},
                         'meta': {'modified_at': '2017-07-27T18:06:03+00:00'}}}
    assert data == expected
