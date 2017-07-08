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

@pytest.fixture(scope='module')
def testdata(createdb):
    """
    Create the necessary test data for this module.
    :param models.db createdb: pytest fixture for database module
    :return list(str): List of emails for Logins created.
    """
    dbsession = createdb.connect()
    emails = []
    data = ({'full_name': 'f4d94fd2 c10282e403d0', 'email': 'fca7@485d.b169',
             'password': '0c37f17b-4f89-4dce-a453-887b5acb9848'},
            {'full_name': 'e3391b5 586ecf591968', 'email': 'ca14@4891.92d7',
             'password': '7a1bb392-cc9c-4cde-8c9d-9ae2dc638bbf'})
    for record in data:
        profile = profiles.Profiles(full_name=record['full_name'], email=record['email'])
        login = logins.Logins(password=record['password'], profile=profile)
        dbsession.add(login)
        emails.append(profile.email)

    dbsession.commit()
    createdb.close()
    return emails

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

def test_password_blank():
    """ Blank passwords aren't allowed. """
    with pytest.raises(ValueError):
        logins.Logins(password='')

    inst = logins.Logins()
    with pytest.raises(ValueError):
        inst.password = ''

def test_password_short():
    """ Short passwords aren't allowed. """
    with pytest.raises(ValueError):
        logins.Logins(password='abcd12345')

    inst = logins.Logins()
    with pytest.raises(ValueError):
        inst.password = 'abcde1234'

def test_password_email():
    """ Passwords aren't allowed to match email. """
    with pytest.raises(ValueError):
        logins.Logins(password='a703@4285.b5c8', email='a703@4285.b5c8')

    inst1 = logins.Logins(email='e100@441b.b5d7')
    with pytest.raises(ValueError):
        inst1.password = 'e100@441b.b5d7'

    inst2 = logins.Logins(password='48c5@4664.82aa')
    with pytest.raises(ValueError):
        inst2.email = '48c5@4664.82aa'

def test_password_validation():
    """ Getting and setting password. """
    passwd = '99e7988b-578c-4edb-8a28-4831cd47617a'
    inst = logins.Logins(password=passwd)

    assert inst.is_valid_password('') is False
    assert inst.is_valid_password(passwd[:10]) is False
    assert inst.is_valid_password(passwd) is True

def test_person_relation(dbsession):  # pylint: disable=unused-argument
    """
    Profiles can have a Logins relation.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles(full_name='a142cb03 6b369b6bfd1e', email='7aa3@49fa.809b')
    login = logins.Logins(password='84600a2f-0dd1-402a-8e19-5a3c3f27e972')

    assert login.profile is None
    login.profile = profile
    assert login.profile == profile

def test_required_fields_blank(dbsession):
    """
    Logins must have a password and an email address.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    login = logins.Logins()
    login.save()

    # password and email are blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_password(dbsession):
    """
    Logins must have a password and an email address.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    login = logins.Logins(email='7056@4de1.8dd4')
    login.save()

    # password is blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_email(dbsession):
    """
    Logins must have a password and an email address.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    login = logins.Logins(password='eba7f929-5869-41a7-a459-450ba25d7777')
    login.save()

    # email is blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_fields(dbsession):
    """
    Logins must have a password and an email address.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    login = logins.Logins(password='b37f50b0-ef76-4c1b-957c-210a54fc94cd', email='f2c7@4109.9360')
    login.save()

    # Profile associated with email is missing.
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_get_by_email_blank(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Blanks shouldn't be found
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    # Include testdata so we know there are at least some records in table to search
    assert logins.Logins.get_by_email('') is None

def test_get_by_email_unknown(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Non-existing logins shouldn't be found
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    assert '184b@4e19.b8f3' not in testdata
    assert logins.Logins.get_by_email('184b@4e19.b8f3') is None

def test_get_by_email(dbsession):  # pylint: disable=unused-argument
    """
    Create Logins, and then fetch them by email address.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    login = logins.Logins(password='01a1cd60-8608-4bbf-a0da-0922bc6762be')
    login.profile = profiles.Profiles(full_name='fb000987 2e2cb7f95b6a', email='9a12@49e4.88b7')

    # Unsaved logins shouldn't be found
    assert logins.Logins.get_by_email('9a12@49e4.88b7') is None

    login.save()

    # Now it can be found.
    assert logins.Logins.get_by_email('9a12@49e4.88b7') is login

def test_required_profile_missing(dbsession):
    """
    Login profile not existing is an error.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    login = logins.Logins(password='7cc64abd-86bd-4856-8577-5f1123f28cac', email='372d@417c.b9db')
    profile = profiles.Profiles(full_name='5f904cb5 3dad7d54b87b', email='372d@417c.b9db')
    login.save()  # Profile isn't saved because we didn't use the relationship attribute.
    assert login.email == profile.email

    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_profile(dbsession):
    """
    Logins profile must exist.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    login = logins.Logins(password='6d332e7d-0c83-43c3-9fab-ad24c793fd5e')
    profile = profiles.Profiles(full_name='9ca81d5c 42badee25c18', email='3aea@4cbb.a004')
    login.profile = profile
    login.save()
    assert login.email is None

    dbsession.commit()
    assert login.email == profile.email
