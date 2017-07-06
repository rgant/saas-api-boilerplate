"""
Tests for the Base Model
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

import sqlalchemy as sa

from models import base


warnings.simplefilter("error")  # Make All warnings errors while testing.


class DummyBase(base.Base):  # pylint: disable=too-few-public-methods
    """ Model for testing the declarative base. """
    pkey = sa.Column(sa.Integer, primary_key=True)  # SQLAlchemy requires a primary key


class DummyModel(base.BaseModel):
    """ Model for testing the BaseModel. """
    email = sa.Column(sa.String(50), unique=True, nullable=False)


def test_base_str():
    """ String representation of the Base and BaseModel. """
    assert str(DummyBase()) == 'tests.models.test_base.DummyBase'
    assert str(DummyModel()) == 'tests.models.test_base.DummyModel'

def test_base_tablename():
    """ Convert Class Name to snake case for table name. """
    dbase = DummyBase()
    assert dbase.__tablename__ == 'dummy_base'
    model = DummyModel()
    assert model.__tablename__ == 'dummy_model'

def test_base_repr():
    """ Representation of Base and BaseModel should represent python to generate model. """
    dbase = DummyBase()
    assert repr(dbase) == ('tests.models.test_base.DummyBase(created_at=<not loaded>, '
                           'updated_at=<not loaded>, pkey=<not loaded>)')
    model = DummyModel()
    assert repr(model) == ('tests.models.test_base.DummyModel(created_at=<not loaded>, '
                           'updated_at=<not loaded>, id=<not loaded>, email=<not loaded>)')

def test_basemodel_save(dbsession):  # pylint: disable=unused-argument
    """ BaseModels are Session Aware and save themselves. """
    model = DummyModel(email='7cf0@496d.aa5e')
    model.save()
    assert model.id is None

def test_basemodel_get_pk(dbsession):
    """ BaseModels have a get_by_pk method. """
    # First create a record to fetch.
    model = DummyModel(email='9f1c@4dd6.b647')
    model.save()
    dbsession.commit()
    assert model.id is not None
    the_id = model.id

    model2 = DummyModel.get_by_pk(the_id)
    assert model2 == model

def test_basemodel_delete(dbsession):
    """ BaseModels are Session Aware and delete temselves. """
    # First create a record to delete.
    model = DummyModel(email='90e1@47e7.aff7')
    model.save()
    dbsession.commit()
    assert model.id is not None
    the_id = model.id

    model.delete()
    assert DummyModel.get_by_pk(the_id) is None
