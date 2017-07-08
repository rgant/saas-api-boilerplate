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
    dbsession = createdb.connect()
    ids = []
    emails = ('9f1c@4dd6.b647', '90e1@47e7.aff7')
    for email in emails:
        dmodel = DummyModel(email=email)
        dbsession.add(dmodel)
        dbsession.flush()
        ids.append(dmodel.id)

    dbsession.commit()
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

def test_basemodel_save(dbsession):  # pylint: disable=unused-argument
    """
    BaseModels are Session Aware and save themselves. They do not flush however.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    dmodel = DummyModel(email='7cf0@496d.aa5e')
    dmodel.save()
    assert dmodel.id is None
    assert dmodel.modified_at is None
    assert dmodel.email == '7cf0@496d.aa5e'

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

def test_basemodel_modified_at(dbsession):
    """
    On commit (or flush) models should have modified_at timestamp set.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    dmodel = DummyModel(email='63ab@4852.8da7')
    dmodel.save()
    dbsession.commit()
    # MySQL doesnt' support microseconds in datetime columns, but PostgreSQL does. Either way
    # comparing them won't work so remove.
    now = datetime.datetime.utcnow().replace(microsecond=0)
    assert dmodel.id is not None
    assert dmodel.email == '63ab@4852.8da7'
    # PostgreSQL includes microseconds, comparing them won't work so remove
    mod_at = dmodel.modified_at.replace(microsecond=0)
    assert mod_at == now
