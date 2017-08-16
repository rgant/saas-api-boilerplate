"""
Tests for Forgot Password Tokens
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

from models import forgot_password_tokens as fpt
from models import logins, profiles


warnings.simplefilter("error")  # Make All warnings errors while testing.

@pytest.fixture(scope='module')
def testdata(createdb):
    """
    Create the necessary test data for this module.
    :param models.db createdb: pytest fixture for database module
    :return list(str): List of tokens for ForgotPasswordTokens created.
    """
    createdb.connect()
    tokens = []
    data = ({'full_name': 'df8df1a4 11162dcd40bb', 'email': 'c7fe@4a45.96d0',
             'password': '83b6143e-1a75-4e31-abcf-c081b0176c28'},
            {'full_name': '61c12783 784c62ee9e56', 'email': '7a58@438f.859e',
             'password': '2faf78ca-0481-4cfe-8273-64de78690acc'},
            {'full_name': '8e75abf5 4ab60edd1e23', 'email': '713e@4723.bc7a',
             'password': '33df41f1-880f-44e2-bc89-7e111cc6a318'})
    for record in data:
        profile = profiles.Profiles(full_name=record['full_name'], email=record['email'])
        login = logins.Logins(password=record['password'], profile=profile)
        token = fpt.ForgotPasswordTokens(login=login)
        createdb.add(token)
        tokens.append(token.token)

    createdb.commit()
    createdb.close()
    return tokens

def test_gen_token():
    """ Should generate a token string matching the pattern. """
    tok_pttrn = re.compile(r'^[0-9a-f]{32}$')
    token = fpt.ForgotPasswordTokens._gen_token()   # pylint: disable=protected-access
    assert tok_pttrn.match(token)

def test_expiration():
    """ Expiration should be 3 days from now. """
    exp_dt = fpt.ForgotPasswordTokens._expiration().replace(microsecond=0)   # pylint: disable=protected-access
    assert exp_dt == datetime.datetime.utcnow().replace(microsecond=0) + datetime.timedelta(days=3)

def test_new_token_init():
    """ By default new tokens should default to a token and an expiration. """
    token = fpt.ForgotPasswordTokens()
    assert token.token
    assert token.expiration_dt

def test_required_login_missing(dbsession):
    """
    Tokens without a login relationship should error.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    token = fpt.ForgotPasswordTokens()
    token.save()
    assert token.login_id is None

    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_login(dbsession):
    """
    Tokens must have a login relation (which must have a profile relation).
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles(full_name='f4e074b5 15503d6feef0', email='01eb@47b4.9acb')
    login = logins.Logins(password='dd621e4f-194d-442c-bf3d-e1805010486e', profile=profile)
    token = fpt.ForgotPasswordTokens(login=login)
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
    assert fpt.ForgotPasswordTokens.get_by_token('') is None

def test_get_by_token_unknown(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Non-existing tokens shouldn't be found
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    assert '159a5fdbe652476bbf7446183f0d787b' not in testdata
    assert fpt.ForgotPasswordTokens.get_by_token('159a5fdbe652476bbf7446183f0d787b') is None

def test_get_by_token_expired(dbsession, testdata):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Expired tokens shouldn't be returned by get_by_token.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    :param list(str) testdata: pytest fixture listing test data tokens.
    """
    exp_dt = datetime.datetime.utcnow().replace(microsecond=0) - datetime.timedelta(days=3,
                                                                                    seconds=1)
    token = fpt.ForgotPasswordTokens.get_by_token(testdata[2])
    token.expiration_dt = exp_dt  # expire the token
    token.save()

    # Expired so it cannot be found.
    assert fpt.ForgotPasswordTokens.get_by_token(token.token) is None

def test_get_by_token(dbsession):  # pylint: disable=unused-argument
    """
    Create ForgotPasswordTokens.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles(full_name='7aad753a bf457864c212', email='3525@45d7.b541')
    login = logins.Logins(password='9c73cd45-f522-4b0d-9948-e87fc791fe93', profile=profile)
    token = fpt.ForgotPasswordTokens(login=login)

    # Unsaved tokens shouldn't be found
    assert fpt.ForgotPasswordTokens.get_by_token(token.token) is None

    token.save()

    # Now it can be found.
    assert fpt.ForgotPasswordTokens.get_by_token(token.token) is token
