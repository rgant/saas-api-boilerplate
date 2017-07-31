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
import sqlalchemy.orm as saorm

from models import bases
import ourmarshmallow


warnings.simplefilter("error")  # Make All warnings errors while testing.

class FakeRelation(bases.BaseModel):
    """ Has many FakeModels relatinships. """
    email = sa.Column(sa.String(50), unique=True, nullable=False)

    fake_models = saorm.relationship('FakeModel', back_populates='fake_relation')


class FakeModel(bases.BaseModel):
    """ Has one FakeRelation relationship. """
    # Because this is a ForeignKey Marshmallow-SQLAlchemy won't include it by default.
    email = sa.Column(sa.String(50), sa.ForeignKey('fake_relation.email'), nullable=False)
    full_name = sa.Column(sa.String(100), nullable=False)

    fake_relation = saorm.relationship('FakeRelation', back_populates='fake_models')


class FakeRelationSchema(ourmarshmallow.Schema):
    """ For testing schemas. """
    class Meta(object):  # pylint: disable=missing-docstring,too-few-public-methods
        model = FakeRelation


class FakeModelSchema(ourmarshmallow.Schema):
    """ For testing schemas. """
    class Meta(object):  # pylint: disable=missing-docstring,too-few-public-methods
        model = FakeModel
        include_fk = True  # Include the email ForeignKey in Schema


def test_schema_session(dbsession):
    """
    Schemas should have a session on init.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    schema = FakeModelSchema()
    assert schema.session == dbsession

def test_schema_type():
    """
    Schemas should type_ set to kebab-case of model.__name__.
    """
    schema = FakeModelSchema()
    assert schema.opts.type_ == 'fake-model'

def test_schema_strict():
    """ Schema options should default to strict. """
    schema = FakeModelSchema()
    assert schema.strict is True

def test_schema_dump():
    """ Should return JSONAPI envelope for FakeModel. """
    now = datetime.datetime(2017, 7, 27, 18, 6, 3)
    the_model = FakeModel(id='45071', email='8cf0@4fc3.a865', full_name='eed5631b 3bd038939b5c',
                          modified_at=now)
    the_schema = FakeModelSchema()
    data = the_schema.dump(the_model).data
    expected = {'data': {'type': 'fake-model', 'id': '45071',
                         'attributes': {'email': '8cf0@4fc3.a865',
                                        'full-name': 'eed5631b 3bd038939b5c'},
                         'relationships': {'fake-relation': {
                             'links': {'self': '/fake-model/45071/relationships/fake-relation',
                                       'related': '/fake-model/45071/fake-relation'}}},
                         'links': {'self': '/fake-model/45071'},
                         'meta': {'modified_at': '2017-07-27T18:06:03+00:00'}},
                'links': {'self': '/fake-model/45071'}}
    assert data == expected

def test_schema_load(dbsession):  # pylint: disable=unused-argument
    """
    Should unwrap the JSONAPI envelope into a FakeModel. Need a dbsession because load will attempt
    to find an existing fake_model table row for id 19269667 so we must ensure the table exists.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    data = {'data': {'type': 'fake-model', 'id': '19269667',
                     'attributes': {'email': 'd0e0@443a.b9cf',
                                    'full-name': '33bfed85 04af3a57d827'},
                     'meta': {'modified_at': '2017-07-28T17:11:51+00:00'}}}
    the_schema = FakeModelSchema()
    the_model = the_schema.load(data).data
    assert isinstance(the_model, FakeModel)
    assert the_model.id == int(data['data']['id'])
    assert the_model.email == data['data']['attributes']['email']
    assert the_model.full_name == data['data']['attributes']['full-name']
    assert the_model.modified_at is None  # Meta values aren't loaded into the model.
