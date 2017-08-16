"""
Tests for Relationship endpoints.
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

class Departments(bases.BaseModel):
    """ Model for testing relationship endpoints. """
    name = sa.Column(sa.String(50), nullable=False)

    parent_id = sa.Column(sa.Integer(), sa.ForeignKey('departments.id'))

    parent = sa.orm.relationship('Departments', back_populates='children',
                                 remote_side='Departments.id')
    children = sa.orm.relationship('Departments', back_populates='parent')


class DepartmentsSchema(ourmarshmallow.Schema):
    """ Schema for testing relationsship endpoints. """
    class Meta(object):  # pylint: disable=missing-docstring,too-few-public-methods
        model = Departments


class ParentRelationship(ourapi.JsonApiRelationship):
    """ Endpoints for a Persons Relationship. """
    relationship = DepartmentsSchema.field_for('parent')


class ChildrenRelationship(ourapi.JsonApiRelationship):
    """ Endpoints for a children Relationship. """
    relationship = DepartmentsSchema.field_for('children')


@pytest.fixture(scope='module')
def testdata(createdb):
    """
    Create the necessary test data for this module.
    :param models.db createdb: pytest fixture for database module
    """
    createdb.connect()
    now = datetime.datetime(2017, 8, 14, 20, 26, 14)
    data = ({'id': 10, 'name': 'Extension Message', 'parent_id': None},
            {'id': 20, 'name': 'City Beat', 'parent_id': 10},
            {'id': 11, 'name': 'Brown Floor', 'parent_id': 10},
            {'id': 21, 'name': 'Guest Desert', 'parent_id': 20},
            {'id': 22, 'name': 'Priest Headache', 'parent_id': 20})
    for record in data:
        dept = Departments(id=record['id'], name=record['name'], parent_id=record['parent_id'],
                           modified_at=now)
        createdb.add(dept)

    createdb.commit()
    createdb.close()

def test_read_none_relationship(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    To One Relationships without a value should return None as primary data.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ParentRelationship()
    response = resource.get(10)
    # 404 is only for when the relationship doesn't exist, not when the value is empty.
    # http://jsonapi.org/format/#fetching-relationships-responses-200
    assert response == {'data': None, 'links': {'related': '/departments/10/parent',
                                                'self': '/departments/10/relationships/parent'}}

def test_read_to_one_relationship(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Read a to one relationship data.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ParentRelationship()
    response = resource.get(20)
    assert response == {'data': {'id': '10', 'type': 'departments'},
                        'links': {'related': '/departments/20/parent',
                                  'self': '/departments/20/relationships/parent'}}

def test_read_empty_list_relationship(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name,invalid-name
    """
    To Many Relationships without a value should return empty list as primary data.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ChildrenRelationship()
    response = resource.get(22)
    # Just above this section is an example a related resource request returning nothing:
    # http://jsonapi.org/format/#fetching-resources-responses-404
    assert response == {'data': [], 'links': {'related': '/departments/22/children',
                                              'self': '/departments/22/relationships/children'}}

def test_read_to_many_relationship(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Read a to many relationships.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ChildrenRelationship()
    response = resource.get(20)
    assert response == {'data': [{'id': '21', 'type': 'departments'},
                                 {'id': '22', 'type': 'departments'}],
                        'links': {'related': '/departments/20/children',
                                  'self': '/departments/20/relationships/children'}}

def test_model_missing_relationship(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Model ID 999 doesn't exist so this should return a 404 Not Found exception.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    resource = ChildrenRelationship()
    with pytest.raises(NotFound):
        resource.get(999)
