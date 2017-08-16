"""
Tests for the Base Model
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
import sqlalchemy_utils.functions

from models import bases


warnings.simplefilter("error")  # Make All warnings errors while testing.


class DummyBase(bases.Base):  # pylint: disable=too-few-public-methods
    """ Model for testing the declarative base. """
    pkey = sa.Column(sa.Integer, primary_key=True)  # SQLAlchemy requires a primary key


class DummyModel(bases.BaseModel):
    """ Model for testing the BaseModel. """
    email = sa.Column(sa.String(50), unique=True, nullable=False)

@pytest.fixture(scope='module')
def testdata(createdb):
    """
    Create the necessary test data for this module.
    :param models.db createdb: pytest fixture for database module
    :return list(int): List of ids for DummyModel created.
    """
    createdb.connect()
    ids = []
    emails = ('9f1c@4dd6.b647', '90e1@47e7.aff7')
    for email in emails:
        dmodel = DummyModel(email=email)
        createdb.add(dmodel)
        createdb.flush()
        ids.append(dmodel.id)

    createdb.commit()
    createdb.close()
    return ids

def test_base_str():
    """ String representation of the Base and BaseModel. """
    assert str(DummyBase()) == 'tests.models.test_base.DummyBase'
    assert str(DummyModel()) == 'tests.models.test_base.DummyModel'

def test_base_tablename():
    """ Convert Class Name to snake case for table name. """
    dbase = DummyBase()
    assert dbase.__tablename__ == 'dummy_base'
    dmodel = DummyModel()
    assert dmodel.__tablename__ == 'dummy_model'

def test_base_repr():
    """ Representation of Base and BaseModel should represent python to generate model. """
    dbase = DummyBase()
    assert repr(dbase) == ('tests.models.test_base.DummyBase(modified_at=<not loaded>, '
                           'pkey=<not loaded>)')
    dmodel = DummyModel()
    assert repr(dmodel) == ('tests.models.test_base.DummyModel(modified_at=<not loaded>, '
                            'id=<not loaded>, email=<not loaded>)')

def test_base_default_fields():
    """
    All Base and BaseModel should have a modified_at column. BaseModel should have an id column.
    """
    assert not hasattr(DummyBase, 'id')
    assert isinstance(sqlalchemy_utils.functions.get_type(DummyBase.modified_at), sa.DateTime)

    assert isinstance(sqlalchemy_utils.functions.get_type(DummyModel.id), sa.Integer)
    assert isinstance(sqlalchemy_utils.functions.get_type(DummyModel.modified_at), sa.DateTime)

def test_basemodel_save(dbsession):  # pylint: disable=unused-argument
    """
    BaseModels are Session Aware and save themselves. They do not flush by default however.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    dmodel = DummyModel(email='7cf0@496d.aa5e')
    dmodel.save()
    assert dmodel.id is None
    assert dmodel.modified_at is None
    assert dmodel.email == '7cf0@496d.aa5e'

def test_basemodel_save_flush(dbsession):  # pylint: disable=unused-argument
    """
    BaseModels are Session Aware and save themselves this time with flush after save.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    dmodel = DummyModel(email='639f@4054.bca6')
    dmodel.save(flush=True)
    # MySQL doesnt' support microseconds in datetime columns, but PostgreSQL does. Either way
    # comparing them won't work so remove.
    now = datetime.datetime.utcnow().replace(microsecond=0)
    assert dmodel.id == 2
    # PostgreSQL includes microseconds, comparing them won't work so remove
    mod_at = dmodel.modified_at.replace(microsecond=0)
    assert mod_at == now
    assert dmodel.email == '639f@4054.bca6'

def test_basemodel_get_all(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Default should return all of the records in the table.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(int) testdata: pytest fixture listing DummyModel test data ids.
    """
    all_models = DummyModel.get_all()
    assert len(all_models) == 2

def test_basemodel_get_all_filter(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Filter records by conditions.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(int) testdata: pytest fixture listing DummyModel test data ids.
    """
    all_models = DummyModel.get_all({'email': '90e1@47e7.aff7'})
    assert len(all_models) == 1
    assert all_models[0].email == '90e1@47e7.aff7'

def test_basemodel_get_all_empty(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Conditions that cannot be met should return an empty list.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(int) testdata: pytest fixture listing DummyModel test data ids.
    """
    all_models = DummyModel.get_all({'email': 'foo@bar.baz'})
    assert all_models == []

def test_basemodel_get_pk_blank(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Empty IDs should return None
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(int) testdata: pytest fixture listing DummyModel test data ids.
    """
    assert 0 not in testdata
    dmodel = DummyModel.get_by_pk(0)
    assert dmodel is None

def test_basemodel_get_pk_none(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    None IDs should return None
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(int) testdata: pytest fixture listing DummyModel test data ids.
    """
    dmodel = DummyModel.get_by_pk(None)
    assert dmodel is None

def test_basemodel_get_pk_missing(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    None IDs should return None
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(int) testdata: pytest fixture listing DummyModel test data ids.
    """
    assert 123 not in testdata
    dmodel = DummyModel.get_by_pk(123)
    assert dmodel is None

def test_basemodel_get_pk(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    BaseModels have a get_by_pk method.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(int) testdata: pytest fixture listing DummyModel test data ids.
    """
    dmodel = DummyModel.get_by_pk(testdata[0])
    assert dmodel.id == testdata[0]

def test_basemodel_delete(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    BaseModels are Session Aware and delete temselves.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(int) testdata: pytest fixture listing DummyModel test data ids.
    """
    dmodel = DummyModel.get_by_pk(testdata[1])
    dmodel.delete()
    assert DummyModel.get_by_pk(testdata[1]) is None

def test_basemodel_modified_at(dbsession):  # pylint: disable=unused-argument
    """
    On commit (or flush) models should have modified_at timestamp set.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    dmodel = DummyModel(email='63ab@4852.8da7')
    dmodel.save(flush=True)
    # MySQL doesnt' support microseconds in datetime columns, but PostgreSQL does. Either way
    # comparing them won't work so remove.
    now = datetime.datetime.utcnow().replace(microsecond=0)
    assert dmodel.id is not None
    assert dmodel.email == '63ab@4852.8da7'
    # PostgreSQL includes microseconds, comparing them won't work so remove
    mod_at = dmodel.modified_at.replace(microsecond=0)
    assert mod_at == now
