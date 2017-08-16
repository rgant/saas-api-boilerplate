"""
Tests for Authentication Tokens
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import datetime
import re
import warnings

import pytest
from sqlalchemy.exc import IntegrityError

from models import authentication_tokens as autht
from models import logins, profiles


warnings.simplefilter("error")  # Make All warnings errors while testing.

@pytest.fixture(scope='module')
def testdata(createdb):
    """
    Create the necessary test data for this module.
    :param models.db createdb: pytest fixture for database module
    :return list(str): List of tokens for AuthenticationTokens created.
    """
    createdb.connect()
    tokens = []
    data = ({'full_name': '24c6e6a4 960f1df1d6ac', 'email': '7d26@4f1b.a38e',
             'password': 'be4b80d3-a6f2-442e-b495-2161376423ab'},
            {'full_name': '8ad0c442 92728ef096a4', 'email': '6594@4fe0.8d07',
             'password': 'b72da3ad-9b28-4be1-b9b0-9d611d465c31'},
            {'full_name': '5a61452b 2830a9f8c820', 'email': 'a26d@433d.be92',
             'password': '69073f4c-6328-47de-80c5-ab09016c69aa'})
    for record in data:
        profile = profiles.Profiles(full_name=record['full_name'], email=record['email'])
        login = logins.Logins(password=record['password'], profile=profile)
        token = autht.AuthenticationTokens(login=login)
        createdb.add(token)
        tokens.append(token.token)

    createdb.commit()
    createdb.close()
    return tokens

def test_gen_token():
    """ Should generate a token string matching the pattern. """
    tok_pttrn = re.compile(r'^[0-9a-f]{32}$')
    token = autht.AuthenticationTokens._gen_token()   # pylint: disable=protected-access
    assert tok_pttrn.match(token)

def test_expiration():
    """ Expiration should be 3 days from now. """
    exp_dt = autht.AuthenticationTokens._expiration().replace(microsecond=0)   # pylint: disable=protected-access
    assert exp_dt == datetime.datetime.utcnow().replace(microsecond=0) + \
        datetime.timedelta(minutes=30)

def test_new_token_init():
    """ By default new tokens should default to a token and an expiration. """
    token = autht.AuthenticationTokens()
    assert token.token
    assert token.expiration_dt

def test_required_login_missing(dbsession):
    """
    Tokens without a login relationship should error.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    token = autht.AuthenticationTokens()
    token.save()
    assert token.login_id is None

    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_login(dbsession):
    """
    Tokens must have a login relation (which must have a profile relation).
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles(full_name='3ea4a6ec 7bb15fa70936', email='4523@45dc.a65b')
    login = logins.Logins(password='447c5f94-e889-4d84-89f4-b195adfd737c', profile=profile)
    token = autht.AuthenticationTokens(login=login)
    token.save()
    assert token.login_id is None

    dbsession.commit()
    assert token.login == login

def test_get_by_token_blank(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Blanks shouldn't be found
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    # Include testdata so we know there are at least some records in table to search
    assert autht.AuthenticationTokens.get_by_token('') is None

def test_get_by_token_unknown(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Non-existing tokens shouldn't be found
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    assert 'ec68a3ba9541497f91c79df62ba4575d' not in testdata
    assert autht.AuthenticationTokens.get_by_token('ec68a3ba9541497f91c79df62ba4575d') is None

def test_get_by_token_expired(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Expired tokens shouldn't be returned by get_by_token.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    exp_dt = datetime.datetime.utcnow().replace(microsecond=0) - datetime.timedelta(minutes=30,
                                                                                    seconds=1)
    token = autht.AuthenticationTokens.get_by_token(testdata[2])
    token.expiration_dt = exp_dt  # expire the token
    token.save()

    # Expired so it cannot be found.
    assert autht.AuthenticationTokens.get_by_token(token.token) is None

def test_get_by_token(dbsession):  # pylint: disable=unused-argument
    """
    Create AuthenticationTokens.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles(full_name='8afcc6f0 34086c4efc7c', email='51f2@4280.931e')
    login = logins.Logins(password='715566ec-0f81-446f-a5f4-74f775fb008a', profile=profile)
    token = autht.AuthenticationTokens(login=login)

    # Unsaved tokens shouldn't be found
    assert autht.AuthenticationTokens.get_by_token(token.token) is None

    token.save()

    # Now it can be found.
    assert autht.AuthenticationTokens.get_by_token(token.token) is token
