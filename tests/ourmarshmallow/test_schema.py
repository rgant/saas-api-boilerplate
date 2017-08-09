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

import marshmallow
import pytest
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
        listable = True


class FakeModelSchema(ourmarshmallow.Schema):
    """ For testing schemas. """
    class Meta(object):  # pylint: disable=missing-docstring,too-few-public-methods
        model = FakeModel
        include_fk = True  # Include the email ForeignKey in Schema


def test_schema_opt_class():
    """ Schema should default to our SchemaOpts class. """
    schema = FakeModelSchema()
    assert issubclass(schema.OPTIONS_CLASS, ourmarshmallow.schema.SchemaOpts)

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

def test_schema_converter():
    """ Schema should use our custom ModelConverter to support JSONAPI Relationship fields. """
    schema = FakeModelSchema()
    assert issubclass(schema.opts.model_converter, ourmarshmallow.convert.ModelConverter)

def test_schema_self_url():
    """ Schema self_url and self_url_kwargs should be automatically set from model name. """
    schema = FakeModelSchema()
    assert schema.opts.self_url == f'/{schema.opts.type_}/{{id}}'
    assert schema.opts.self_url_kwargs == {'id': '<id>'}

def test_schema_listable_default():
    """ By default the listable option should be False. """
    schema = FakeModelSchema()
    assert schema.opts.listable is False
    assert schema.opts.self_url_many is None

def test_schema_self_url_many():
    """
    Setting the listable option on schema should also set the self_url_many option automatically.
    """
    schema = FakeRelationSchema()
    assert schema.opts.listable is True
    assert schema.opts.self_url_many == f'/{schema.opts.type_}'
    assert schema.opts.self_url.startswith(schema.opts.self_url_many)

def test_schema_inflect():
    """ attribute inflection should convert snake_case names to kebab-case. """
    schema = FakeModelSchema()
    test_strings = {
        'test': 'test',
        'Test': 'Test',
        'TEST': 'TEST',
        'snakes_On_A_Plane': 'snakes-On-A-Plane',
        'Snakes_On_A_Plane': 'Snakes-On-A-Plane',
        'snakes_on_a_plane': 'snakes-on-a-plane',
        'I_Phone_Hysteria': 'I-Phone-Hysteria',
        'i_phone_hysteria': 'i-phone-hysteria',
        '_Test': '-Test',
        '_test_Method': '-test-Method',
        '__test__Method': '--test--Method',
        '__CamelCase': '--CamelCase',
        '_Camel_Case': '-Camel-Case'
    }

    for snake, dasher in test_strings.items():
        assert schema.inflect(snake) == dasher

def test_schema_default_columns():
    """ All Schemas should default to an id and modified_at field. """
    schema = FakeModelSchema()
    assert isinstance(schema.declared_fields['id'], ourmarshmallow.fields.Integer)
    assert schema.declared_fields['id'].as_string is True
    assert isinstance(schema.declared_fields['modified_at'], ourmarshmallow.fields.MetaData)
    assert isinstance(schema.declared_fields['modified_at'].container,
                      ourmarshmallow.fields.DateTime)

def test_schema_dump():
    """ Should return JSONAPI envelope for FakeModel. """
    now = datetime.datetime(2017, 7, 27, 18, 6, 3)
    the_model = FakeModel(id=45071, email='8cf0@4fc3.a865', full_name='eed5631b 3bd038939b5c',
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

def test_schema_load_without_id():
    """ id isn't required on load. """
    data = {'data': {'type': 'fake-model',
                     'attributes': {'email': '0a97@4e42.994d',
                                    'full-name': '8e8ac2d1 2e7904048885'}}}
    the_schema = FakeModelSchema()
    the_model = the_schema.load(data).data
    assert isinstance(the_model, FakeModel)
    assert the_model.id is None
    assert the_model.email == data['data']['attributes']['email']
    assert the_model.full_name == data['data']['attributes']['full-name']

def test_instance_requires_id():
    """ When loading schemas into an existing instance the id must exist. """
    the_model = FakeModel(id=4, email='3c6e@4638.9834', full_name='79826dc9 f864dee2dbe7')

    data = {'data': {'type': 'fake-model', 'id': '4',
                     'attributes': {'email': 'ba40@4c91.8ba4',
                                    'full-name': '9ffc634b d9f11b47cf97'}}}
    the_schema = FakeModelSchema()
    the_schema.load(data, instance=the_model)
    assert the_model.id == 4
    assert the_model.email == data['data']['attributes']['email']
    assert the_model.full_name == data['data']['attributes']['full-name']

def test_instance_missing_id():
    """ Error should be raised when id is missing from data in schema load with instance. """
    the_model = FakeModel(id=7, email='cc66@44ab.994f', full_name='75fea687 10dcd18e4b74')

    data = {'data': {'type': 'fake-model',
                     'attributes': {'email': '443d@4e0b.8eb1',
                                    'full-name': 'a72f6d46 fa4a23cc0750'}}}
    the_schema = FakeModelSchema()
    with pytest.raises(marshmallow.ValidationError):
        the_schema.load(data, instance=the_model)

    assert the_model.email == 'cc66@44ab.994f'
    assert the_model.full_name == '75fea687 10dcd18e4b74'

def test_instance_mismatched_id():
    """ Error should be raised when id from data in schema load doesn't match the instance id. """
    the_model = FakeModel(id=3, email='4271@4f2c.a021', full_name='a7fbacd4 4948b217d9b6')

    data = {'data': {'type': 'fake-model', 'id': '1',
                     'attributes': {'email': '03d8@4e3c.af63',
                                    'full-name': '3a9b905d bd1be0b0f5e9'}}}
    the_schema = FakeModelSchema()
    with pytest.raises(ourmarshmallow.exceptions.MismatchIdError):
        the_schema.load(data, instance=the_model)

    assert the_model.email == '4271@4f2c.a021'
    assert the_model.full_name == 'a7fbacd4 4948b217d9b6'
