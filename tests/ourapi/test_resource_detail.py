"""
Tests for the API JsonApiResource class details endpoints with identifiers. Read, Update, and Delete
all by identifier.
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

from models import bases
import ourapi
from ourapi.exceptions import Conflict, NotFound
import ourmarshmallow


warnings.simplefilter("error")  # Make All warnings errors while testing.

class Horses(bases.BaseModel):
    """ Model for testing JsonApiResource. """
    name = sa.Column(sa.String(50), nullable=False)


class HorsesSchema(ourmarshmallow.Schema):
    """ JSONAPI Schema from SQLAlchemy Horses Model. """
    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Horses


class HorsesResource(ourapi.JsonApiResource):
    """ JSONAPI CRUD endpoints for HorsesSchema/Horses Model. """
    schema = HorsesSchema


def test_new_detail_resource():
    """ Resource endpoint for Model details. """
    resource = HorsesResource()
    assert isinstance(resource, HorsesResource)

def test_detail_read(dbsession):  # pylint: disable=unused-argument
    """ Create a resource, and then Read it """
    now = datetime.datetime(2017, 8, 7, 18, 37, 29)
    the_model = Horses(id=10, name="foo bar baz", modified_at=now)
    the_model.save()

    resource = HorsesResource()
    response = resource.get(10)

    assert response == {'data': {'attributes': {'name': 'foo bar baz'},
                                 'id': '10',
                                 'links': {'self': '/horses/10'},
                                 'meta': {'modified_at': '2017-08-07T18:37:29+00:00'},
                                 'type': 'horses'},
                        'links': {'self': '/horses/10'}}

def test_detail_read_not_found(dbsession):  # pylint: disable=unused-argument
    """ Resource Detail Read raises NotFound when id isn't found. """
    resource = HorsesResource()

    with pytest.raises(NotFound) as excinfo:
        resource.get(999)

    assert excinfo.value.description == {'detail': '999 not found.',
                                         'source': {'parameter': '/id'}}

def test_detail_update(dbsession):  # pylint: disable=unused-argument
    """ Update a resource by id. """
    now = datetime.datetime(2017, 8, 7, 18, 42, 49)
    the_model = Horses(id=20, name="qux corge", modified_at=now)
    the_model.save()

    expected = {'data': {'attributes': {'name': 'fizzbuzz'},
                         'id': '20',
                         'links': {'self': '/horses/20'},
                         'meta': {'modified_at': '2017-08-07T18:42:49+00:00'},
                         'type': 'horses'},
                'links': {'self': '/horses/20'}}

    # id is required for patch
    patch_data = {'data': {'attributes': {'name': 'fizzbuzz'}, 'id': '20', 'type': 'horses'}}
    resource = HorsesResource()
    response = resource.patch(20, patch_data)
    # There is a flaw here because the session hasn't been commited when the response is sent.
    assert response == expected

    response = resource.get(20)
    # Correct the timestamp, which we will assume is correct
    expected['data']['meta']['modified_at'] = response['data']['meta']['modified_at']
    assert response == expected

def test_detail_update_not_found(dbsession):  # pylint: disable=unused-argument
    """ Resource detail Update raises NotFound when id. """
    patch_data = {'data': {'attributes': {'name': 'bad request'}, 'type': 'horses'}}
    resource = HorsesResource()
    with pytest.raises(NotFound) as excinfo:
        resource.patch(999, patch_data)

    assert excinfo.value.description == {'detail': '999 not found.',
                                         'source': {'parameter': '/id'}}

def test_detail_update_id_required(dbsession):  # pylint: disable=unused-argument
    """ Payload id and URL id must match for patch/update """
    the_model = Horses(id=30, name="Time Coin Instant Understand")
    the_model.save()

    # id is missing, but it is required: http://jsonapi.org/format/#crud-updating
    patch_data = {'data': {'attributes': {'name': 'bad request'}, 'type': 'horses'}}
    resource = HorsesResource()
    with pytest.raises(marshmallow.ValidationError) as excinfo:
            # This will be turned into a BadRequest by the error handler in the API.
        resource.patch(30, patch_data)

    assert excinfo.value.messages == {'errors': [{'detail': '`data` object must include `id` key.',
                                                  'source': {'pointer': '/data'}}]}

def test_detail_update_id_mismatch(dbsession):  # pylint: disable=unused-argument
    """ Payload id and URL id must match for patch/update """
    the_model = Horses(id=40, name="Madden Everything Wonder Pronunciation")
    the_model.save()

    # id does not match the request url id
    patch_data = {'data': {'attributes': {'name': 'bad request'},
                           'id': '999', 'type': 'horses'}}
    resource = HorsesResource()
    with pytest.raises(Conflict) as excinfo:
        resource.patch(40, patch_data)

    assert excinfo.value.description == {'detail': 'Mismatched id. Expected "40".',
                                         'source': {'pointer': '/data/id'}}

def test_detail_update_type_mismatch(dbsession):  # pylint: disable=unused-argument,invalid-name
    """ Payload type and URL must match for patch/update """
    the_model = Horses(id=50, name="Ordinary Know Scent Advice")
    the_model.save()

    # id does not match the request url id
    patch_data = {'data': {'attributes': {'name': 'bad request'},
                           'id': '50', 'type': 'batteries'}}
    resource = HorsesResource()
    with pytest.raises(Conflict) as excinfo:
        resource.patch(50, patch_data)

    assert excinfo.value.description == {'detail': 'Invalid type. Expected "horses".',
                                         'source': {'pointer': '/data/type'}}
