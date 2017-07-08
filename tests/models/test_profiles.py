"""
Tests for the Profiles Model
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

import pytest
from sqlalchemy.exc import IntegrityError

from models import logins, profiles


warnings.simplefilter("error")  # Make All warnings errors while testing.

@pytest.fixture(scope='module')
def testdata(createdb):
    """
    Create the necessary test data for this module.
    :param models.db createdb: pytest fixture for database module
    :return list(str): List of emails for Profiles created.
    """
    dbsession = createdb.connect()
    emails = []
    data = ({'full_name': '4961e0b7 9acfd7e74533', 'email': '439b@47e7.ae97'},
            {'full_name': '315ab3db 535af6a5b009', 'email': '8d3d@4719.8278'})
    for record in data:
        profile = profiles.Profiles(full_name=record['full_name'], email=record['email'])
        dbsession.add(profile)
        emails.append(profile.email)

    dbsession.commit()
    createdb.close()
    return emails

def test_email_validation_none():
    """ None is not a valid email value """
    with pytest.raises(TypeError):
        profiles.Profiles(email=None)

    inst = profiles.Profiles()
    with pytest.raises(TypeError):
        inst.email = None

def test_email_validation_blank():
    """ Blanks are not allowed """
    with pytest.raises(ValueError):
        profiles.Profiles(email='')

    inst = profiles.Profiles()
    with pytest.raises(ValueError):
        inst.email = ''

def test_email_validation_bademail():
    """ email address must be valid. """
    with pytest.raises(ValueError):
        profiles.Profiles(email='bademail')

    inst = profiles.Profiles()
    with pytest.raises(ValueError):
        inst.email = 'otherbademail'

def test_email_validation():
    """ Must be a valid email address in model. """
    inst1 = profiles.Profiles(email='3837@4ab6.bf84')
    assert inst1.email == '3837@4ab6.bf84'

    # You can create model without an email
    inst2 = profiles.Profiles()
    inst2.email = 'f0ad@4f94.ab7d'
    assert inst2.email == 'f0ad@4f94.ab7d'

def test_required_fields_blank(dbsession):
    """
    Profiles must have a full_name and an email address.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles()
    profile.save()

    # full_name and email are blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_password(dbsession):
    """
    Profiles must have a full_name and an email address.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles(email='7056@4de1.8dd4')
    profile.save()

    # full_name is blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_email(dbsession):
    """
    Profiles must have a full_name and an email address.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles(full_name='a79b8cae 76fdda035a30')
    profile.save()

    # email is blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_fields(dbsession):
    """
    Profiles must have a full_name and an email address.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles(full_name='07694435 6b04b7cda98c', email='b9ea@4182.a914')
    profile.save()

    dbsession.commit()

def test_get_by_email_blank(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Blanks shouldn't be found
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    # Include testdata so we know there are at least some records in table to search
    assert profiles.Profiles.get_by_email('') is None

def test_get_by_email_unknonw(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Non-existing profiles shouldn't be found
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    assert '1ced@4c41.a936' not in testdata
    assert profiles.Profiles.get_by_email('1ced@4c41.a936') is None

def test_get_by_email(dbsession):  # pylint: disable=unused-argument
    """ Create Profiles, and then fetch them by email address. """
    profile = profiles.Profiles(full_name='7cfeb824 a59fafe0f656', email='2c32@4fc0.beec')

    # Unsaved profiles shouldn't be found
    assert profiles.Profiles.get_by_email('2c32@4fc0.beec') is None

    profile.save()

    # Now it can be found.
    assert profiles.Profiles.get_by_email('2c32@4fc0.beec') == profile

def test_login_relation(dbsession):  # pylint: disable=unused-argument
    """ Profiles can have a Logins relation. """
    profile = profiles.Profiles(full_name='4176898b 61d515c6e423', email='61b4@4a1d.9f2b')
    login = logins.Logins(password='104d4cec-9425-4e37-9de2-242c6d772eea')

    assert profile.login is None
    profile.login = login
    assert profile.login == login
