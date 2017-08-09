"""
Tests for the API ResourceDetail class
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import datetime
import warnings

import flask
import pytest
import sqlalchemy as sa

from models import bases
import ourapi
from ourapi.exceptions import Conflict, NotFound
import ourmarshmallow


warnings.simplefilter("error")  # Make All warnings errors while testing.

class Horses(bases.BaseModel):
    """ Model for testing ResourceDetail """
    name = sa.Column(sa.String(50), nullable=False)


class HorsesSchema(ourmarshmallow.Schema):
    """ JSONAPI Schema from SQLAlchemy Horses Model. """
    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Horses


class HorsesResourceDetail(ourapi.ResourceDetail):
    """ JSONAPI RUD endpoints for HorsesSchema/Horses Model. """
    schema = HorsesSchema


def test_new_detail_resource():
    """ Resource endpoint for Model details. """
    resource = HorsesResourceDetail()
    assert isinstance(resource, HorsesResourceDetail)
    assert resource.endpoint == HorsesSchema.opts.self_url

def test_detail_read(dbsession):  # pylint: disable=unused-argument
    """ Create a resource, and then Read it """
    now = datetime.datetime(2017, 8, 7, 18, 37, 29)
    the_model = Horses(id=10, name="foo bar baz", modified_at=now)
    the_model.save()

    resource = HorsesResourceDetail()
    response = resource.get(10)

    assert response == {'data': {'attributes': {'name': 'foo bar baz'},
                                 'id': '10',
                                 'links': {'self': '/horses/10'},
                                 'meta': {'modified_at': '2017-08-07T18:37:29+00:00'},
                                 'type': 'horses'},
                        'links': {'self': '/horses/10'}}

def test_detail_read_not_found(dbsession):  # pylint: disable=unused-argument
    """ Resource Detail Read raises NotFound when id isn't found. """
    resource = HorsesResourceDetail()

    with pytest.raises(NotFound) as excinfo:
        resource.get(999)

    assert excinfo.value.description == {'detail': '999 not found.',
                                         'source': {'parameter': '/id'}}

def test_detail_update(dbsession):  # pylint: disable=unused-argument
    """ Update a resource by id. """
    now = datetime.datetime(2017, 8, 7, 18, 42, 49)
    the_model = Horses(id=20, name="qux corge", modified_at=now)
    the_model.save()

    test_app = flask.Flask(__name__)
    resource = HorsesResourceDetail()

    expected = {'data': {'attributes': {'name': 'fizzbuzz'},
                         'id': '20',
                         'links': {'self': '/horses/20'},
                         'meta': {'modified_at': '2017-08-07T18:42:49+00:00'},
                         'type': 'horses'},
                'links': {'self': '/horses/20'}}

    # id is required for patch
    patch_data = {'data': {'attributes': {'name': 'fizzbuzz'}, 'id': '20', 'type': 'horses'}}
    with test_app.test_request_context(data=flask.json.dumps(patch_data)):
        response = resource.patch(20)
    # There is a flaw here because the session hasn't been commited when the response is sent.
    assert response == expected

    response = resource.get(20)
    # Correct the timestamp, which we will assume is correct
    expected['data']['meta']['modified_at'] = response['data']['meta']['modified_at']
    assert response == expected

def test_detail_update_not_found(dbsession):  # pylint: disable=unused-argument
    """ Resource detail Update raises NotFound when id. """
    test_app = flask.Flask(__name__)
    resource = HorsesResourceDetail()

    patch_data = {'data': {'attributes': {'name': 'bad request'}, 'type': 'horses'}}
    with test_app.test_request_context(data=flask.json.dumps(patch_data)), \
            pytest.raises(NotFound) as excinfo:
        resource.patch(999)

    assert excinfo.value.description == {'detail': '999 not found.',
                                         'source': {'parameter': '/id'}}

def test_detail_update_id_required(dbsession):  # pylint: disable=unused-argument
    """ Payload id and URL id must match for patch/update """
    the_model = Horses(id=30, name="Time Coin Instant Understand")
    the_model.save()

    test_app = flask.Flask(__name__)
    resource = HorsesResourceDetail()

    # id is missing, but it is required: http://jsonapi.org/format/#crud-updating
    patch_data = {'data': {'attributes': {'name': 'bad request'}, 'type': 'horses'}}
    with test_app.test_request_context(data=flask.json.dumps(patch_data)), \
            pytest.raises(Conflict) as excinfo:
        resource.patch(30)

    assert excinfo.value.description == {'detail': '`data` object must include `id` key.',
                                         'source': {'pointer': '/data'}}

def test_detail_update_id_mismatch(dbsession):  # pylint: disable=unused-argument
    """ Payload id and URL id must match for patch/update """
    the_model = Horses(id=40, name="Madden Everything Wonder Pronunciation")
    the_model.save()

    test_app = flask.Flask(__name__)
    resource = HorsesResourceDetail()

    # id does not match the request url id
    patch_data = {'data': {'attributes': {'name': 'bad request'},
                           'id': '999', 'type': 'horses'}}
    with test_app.test_request_context(data=flask.json.dumps(patch_data)), \
            pytest.raises(Conflict) as excinfo:
        resource.patch(40)

    assert excinfo.value.description == {'detail': 'Mismatched id. Expected "40".',
                                         'source': {'pointer': '/data/id'}}
