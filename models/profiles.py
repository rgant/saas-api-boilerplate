"""
Profiles resources. Separate out the concept of Logins and Profiles which combined make a user.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import sqlalchemy as sa
import sqlalchemy.orm as saorm

from common import utilities
from . import bases
from . import db


class Profiles(bases.BaseModel):
    """ Contains the profile information for a user in the app. """
    email = sa.Column(sa.String(50), unique=True, nullable=False)
    full_name = sa.Column(sa.String(100), nullable=False)

    login = saorm.relationship('Logins', uselist=False, back_populates='profile')
    memberships = saorm.relationship('Memberships', back_populates='profile')

    @classmethod
    def get_by_email(cls, email):
        """
        Lookup Profile by email address.
        :param str email: email address to lookup
        :return Profiles: Matching Profile or None
        """
        return db.query(cls).filter(cls.email == email).one_or_none()

    @saorm.validates('email')
    def validate_email(self, key, address):  # pylint: disable=unused-argument,no-self-use
        """
        :param str key: name of the field to validate.
        :param str address: email address
        :return str: the email address
        :raises ValueError: Invalid email
        """
        if not utilities.is_valid_email_address(address):
            raise ValueError('Invalid Email Address')
        return address
