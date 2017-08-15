"""
Tests for Related model endpoints.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import datetime
import warnings

import pytest
import sqlalchemy as sa

from models import bases
import ourapi
from ourapi.exceptions import NotFound
import ourmarshmallow


warnings.simplefilter("error")  # Make All warnings errors while testing.

class Persons(bases.BaseModel):
    """ Model for testing relations endpoints. """
    name = sa.Column(sa.String(50), nullable=False)

    parent_id = sa.Column(sa.Integer(), sa.ForeignKey('persons.id'))

    parent = sa.orm.relationship('Persons', back_populates='children', remote_side='Persons.id')
    children = sa.orm.relationship('Persons', back_populates='parent')


class PersonsSchema(ourmarshmallow.Schema):
    """ Schema for testing relations endpoints. """
    class Meta(object):  # pylint: disable=missing-docstring,too-few-public-methods
        model = Persons


class ParentRelation(ourapi.JsonApiRelation):
    """ Endpoints for a Persons Relation Models. """
    relation = PersonsSchema.field_for('parent')


class ChildrenRelation(ourapi.JsonApiRelation):
    """ Endpoints for a children Relation Models. """
    relation = PersonsSchema.field_for('children')


@pytest.fixture(scope='module')
def testdata(createdb):
    """
    Create the necessary test data for this module.
    :param models.db createdb: pytest fixture for database module
    """
    dbsession = createdb.connect()
    now = datetime.datetime(2017, 8, 14, 17, 50, 19)
    data = ({'id': 10, 'name': 'Golden Tail', 'parent_id': None},
            {'id': 20, 'name': 'Extra Agree', 'parent_id': 10},
            {'id': 11, 'name': 'Agent Yesterday', 'parent_id': 10},
            {'id': 21, 'name': 'Impossible Stand', 'parent_id': 20},
            {'id': 22, 'name': 'Carry Cool', 'parent_id': 20})
    for record in data:
        person = Persons(id=record['id'], name=record['name'], parent_id=record['parent_id'],
                         modified_at=now)
        dbsession.add(person)

    dbsession.commit()
    createdb.close()

def test_read_none_relation(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    To One Relations without a value should return None as primary data.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ParentRelation()
    response = resource.get(10)
    # Just above this section is an example a related resource request returning nothing:
    # http://jsonapi.org/format/#fetching-resources-responses-404
    assert response == {'data': None, 'links': {'self': '/persons/10/parent'}}

def test_read_to_one_relation(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Read a to one relation model.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ParentRelation()
    response = resource.get(20)
    assert response == {'data': {'attributes': {'name': 'Golden Tail'},
                                 'id': '10',
                                 'links': {'self': '/persons/10'},
                                 'meta': {'modified_at': '2017-08-14T17:50:19+00:00'},
                                 # pylint: disable=line-too-long
                                 'relationships': {'children': {'links': {'related': '/persons/10/children',
                                                                          'self': '/persons/10/relationships/children'}},
                                                   'parent': {'links': {'related': '/persons/10/parent',
                                                                        'self': '/persons/10/relationships/parent'}}},
                                 'type': 'persons'},
                        'links': {'self': '/persons/20/parent'}}

def test_read_empty_list_relation(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    To Many Relations without a value should return empty list as primary data.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ChildrenRelation()
    response = resource.get(22)
    # Just above this section is an example a related resource request returning nothing:
    # http://jsonapi.org/format/#fetching-resources-responses-404
    assert response == {'data': [], 'links': {'self': '/persons/22/children'}}

def test_read_to_many_relation(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Read a to many relation models.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ChildrenRelation()
    response = resource.get(20)
    assert response == {'data': [{'attributes': {'name': 'Impossible Stand'},
                                  'id': '21',
                                  'links': {'self': '/persons/21'},
                                  'meta': {'modified_at': '2017-08-14T17:50:19+00:00'},
                                  # pylint: disable=line-too-long
                                  'relationships': {'children': {'links': {'related': '/persons/21/children',
                                                                           'self': '/persons/21/relationships/children'}},
                                                    'parent': {'links': {'related': '/persons/21/parent',
                                                                         'self': '/persons/21/relationships/parent'}}},
                                  'type': 'persons'},
                                 {'attributes': {'name': 'Carry Cool'},
                                  'id': '22',
                                  'links': {'self': '/persons/22'},
                                  'meta': {'modified_at': '2017-08-14T17:50:19+00:00'},
                                  # pylint: disable=line-too-long
                                  'relationships': {'children': {'links': {'related': '/persons/22/children',
                                                                           'self': '/persons/22/relationships/children'}},
                                                    'parent': {'links': {'related': '/persons/22/parent',
                                                                         'self': '/persons/22/relationships/parent'}}},
                                  'type': 'persons'}],
                        'links': {'self': '/persons/20/children'}}

def test_model_missing_relation(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Model ID 999 doesn't exist so this should return a 404 Not Found exception.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ChildrenRelation()
    with pytest.raises(NotFound):
        resource.get(999)
