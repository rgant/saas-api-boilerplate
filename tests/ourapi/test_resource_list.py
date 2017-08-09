"""
Tests for the API ResourceList class
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
from ourapi.exceptions import Conflict
import ourmarshmallow


warnings.simplefilter("error")  # Make All warnings errors while testing.

class Batteries(bases.BaseModel):
    """ Model for testing ResourceList. """
    charge = sa.Column(sa.Float, nullable=False)


class BatteriesSchema(ourmarshmallow.Schema):
    """ JSONAPI Schema from SQLAlchemy Batteries Model. """
    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Batteries
        listable = True

class BatteriesResource(ourapi.JsonApiResource):
    """ JSONAPI CR endpoints for BatteriesSchema/Batteries Model. """
    schema = BatteriesSchema


@pytest.fixture(scope='module')
def testdata(createdb):
    """
    Create the necessary test data for this module.
    :param models.db createdb: pytest fixture for database module
    """
    dbsession = createdb.connect()
    now = datetime.datetime(2017, 8, 9, 14, 52, 36)
    data = ({'charge': 73.86805094257771, 'id': 10},
            {'charge': 72.00436375546976, 'id': 20},
            {'charge': 87.28642241669909, 'id': 30})
    for record in data:
        battery = Batteries(id=record['id'], charge=record['charge'], modified_at=now)
        dbsession.add(battery)

    dbsession.commit()
    createdb.close()

def test_new_list_resource():
    """ Resource endpoint for Model list/creation. """
    assert BatteriesSchema.opts.listable is True
    resource = BatteriesResource()
    assert isinstance(resource, BatteriesResource)

def test_list_read_empty(dbsession):  # pylint: disable=unused-argument
    """
    No resources are created yet, so we should get back an empty list.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    resource = BatteriesResource()
    response = resource.get()

    assert response == {'data': [], 'links': {'self': '/batteries'}}

def test_list_read(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Read a list of resources.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = BatteriesResource()
    response = resource.get()

    assert response == {'data': [{'attributes': {'charge': 73.8680509425777},
                                  'id': '10',
                                  'links': {'self': '/batteries/10'},
                                  'meta': {'modified_at': '2017-08-09T14:52:36+00:00'},
                                  'type': 'batteries'},
                                 {'attributes': {'charge': 72.0043637554698},
                                  'id': '20',
                                  'links': {'self': '/batteries/20'},
                                  'meta': {'modified_at': '2017-08-09T14:52:36+00:00'},
                                  'type': 'batteries'},
                                 {'attributes': {'charge': 87.2864224166991},
                                  'id': '30',
                                  'links': {'self': '/batteries/30'},
                                  'meta': {'modified_at': '2017-08-09T14:52:36+00:00'},
                                  'type': 'batteries'}],
                        'links': {'self': '/batteries'}}

def test_create_resource(dbsession):  # pylint: disable=unused-argument
    """
    Create a new Batteries Model.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    resource = BatteriesResource()
    # Need to create a flask app and context so post can generate the URL for new model.
    test_app = flask.Flask(__name__)
    test_app.add_url_rule('/batteries/<int:model_id>',
                          view_func=BatteriesResource.as_view(BatteriesResource.__name__))

    post_data = {'data': {'attributes': {'charge': 88.96770429362424}, 'type': 'batteries'}}
    with test_app.test_request_context():
        response, code, headers = resource.post(post_data)

    assert code == 201
    assert headers == {'Location': '/batteries/1'}
    assert response == {'data': {'attributes': {'charge': 88.96770429362424},
                                 'id': '1',
                                 'links': {'self': '/batteries/1'},
                                 # Correct the timestamp, which we will assume is correct
                                 'meta': {'modified_at': response['data']['meta']['modified_at']},
                                 'type': 'batteries'},
                        'links': {'self': '/batteries/1'}}

def test_create_id_conflict(dbsession):  # pylint: disable=unused-argument
    """
    ourapi doesn't support client generated ids.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    resource = BatteriesResource()
    post_data = {'data': {'attributes': {'charge': 67.88553490220708}, 'type': 'batteries',
                          'id': '50'}}
    with pytest.raises(Conflict) as excinfo:
        resource.post(post_data)

    assert excinfo.value.description == {'detail': '`data` object may not include `id` key.',
                                         'source': {'pointer': '/data/id'}}
