"""
Forgotten Password Tokens resource to allow Login password resetting.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import datetime
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as saorm

from . import bases
from . import db


class ForgotPasswordTokens(bases.BaseModel):
    """ Track tokens used to reset passwords for a User. """
    login_id = sa.Column(sa.Integer, sa.ForeignKey('logins.id', ondelete='CASCADE'), nullable=False)
    token = sa.Column(sa.String(35), nullable=False, index=True)
    expiration_dt = sa.Column(sa.DateTime, nullable=False)

    login = saorm.relationship('Logins')

    def __init__(self, *args, **kwargs):
        if 'token' not in kwargs:
            kwargs['token'] = self._gen_token()
        if 'expiration_dt' not in kwargs:
            kwargs['expiration_dt'] = self._expiration()

        super().__init__(*args, **kwargs)

    @staticmethod
    def _expiration():
        """
        Tokens expire in 3 days from creation by default.
        :return datetime.datetime: DateTime for Token Expiration
        """
        return datetime.datetime.utcnow() + datetime.timedelta(days=3)

    @staticmethod
    def _gen_token():
        """
        Generates a token for password resetting.
        :return str: New token
        """
        return uuid.uuid4().hex

    @classmethod
    def get_by_token(cls, token):
        """
        Select forgot password token record by token. Excluding expired tokens.
        :param str token: hex token string to lookup
        :return ForgotPasswordTokens: Record matching token or None.
        """
        now = datetime.datetime.utcnow()
        return db.query(cls).filter(cls.token == token, cls.expiration_dt >= now).one_or_none()
