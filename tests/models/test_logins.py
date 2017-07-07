"""
Tests for the Logins Model
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

def test_password_setter():
    """ Getting and setting password. """
    inst1 = logins.Logins()

    passwd1 = '9738a470-6693-4968-81b2-2778a494a030'
    assert inst1._password is None  # pylint: disable=protected-access
    inst1.password = passwd1
    assert inst1._password is not None  # pylint: disable=protected-access
    assert inst1.password != passwd1

    passwd2 = 'bd2b45ec-1a4a-41c3-8d2a-6bdf456b4175'
    inst2 = logins.Logins(password=passwd2)
    assert inst2._password is not None  # pylint: disable=protected-access
    assert inst2.password != passwd2

def test_password_validation():
    """ Getting and setting password. """
    passwd = '99e7988b-578c-4edb-8a28-4831cd47617a'
    inst = logins.Logins(password=passwd)

    assert inst.is_valid_password('') is False
    assert inst.is_valid_password(passwd[:10]) is False
    assert inst.is_valid_password(passwd) is True

def test_person_relation(dbsession):  # pylint: disable=unused-argument
    """ Profiles can have a Logins relation. """
    profile = profiles.Profiles(full_name='a142cb03 6b369b6bfd1e', email='7aa3@49fa.809b')
    login = logins.Logins(password='84600a2f-0dd1-402a-8e19-5a3c3f27e972')

    assert login.profile is None
    login.profile = profile
    assert login.profile == profile

def test_required_fields_blank(dbsession):
    """ Logins must have a password and an email address. """
    login = logins.Logins()
    login.save()

    # password and email are blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_password(dbsession):
    """ Logins must have a password and an email address. """
    login = logins.Logins(email='7056@4de1.8dd4')
    login.save()

    # password is blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_email(dbsession):
    """ Logins must have a password and an email address. """
    login = logins.Logins(password='eba7f929-5869-41a7-a459-450ba25d7777')
    login.save()

    # email is blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_fields(dbsession):
    """ Logins must have a password and an email address. """
    login = logins.Logins(password='b37f50b0-ef76-4c1b-957c-210a54fc94cd', email='f2c7@4109.9360')
    login.save()

    # Profile associated with email is missing.
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_get_by_email_blank(dbsession):  # pylint: disable=unused-argument
    """ Blanks shouldn't be found """
    assert logins.Logins.get_by_email('') is None

def test_get_by_email_unknonw(dbsession):  # pylint: disable=unused-argument
    """ Non-existing logins shouldn't be found """
    assert logins.Logins.get_by_email('184b@4e19.b8f3') is None

def test_get_by_email(dbsession):  # pylint: disable=unused-argument
    """ Create Logins, and then fetch them by email address. """
    login = logins.Logins(password='01a1cd60-8608-4bbf-a0da-0922bc6762be')
    login.profile = profiles.Profiles(full_name='fb000987 2e2cb7f95b6a', email='9a12@49e4.88b7')

    # Unsaved logins shouldn't be found
    assert logins.Logins.get_by_email('9a12@49e4.88b7') is None

    login.save()

    # Now it can be found.
    assert logins.Logins.get_by_email('9a12@49e4.88b7') is login

def test_required_profile(dbsession):
    """ Logins must have a password and an email address. """
    login = logins.Logins(password='6d332e7d-0c83-43c3-9fab-ad24c793fd5e')
    profile = profiles.Profiles(full_name='9ca81d5c 42badee25c18', email='3aea@4cbb.a004')
    login.profile = profile
    login.save()
    assert login.email is None

    dbsession.commit()
    assert login.email == profile.email
