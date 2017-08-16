"""
Logins resources. Separate out the concept of Logins and Profiles which combined make a user. This
will allow us to store a password history that will allow us to restrict password re-use, and also
allow us to delete/disable logins while keeping Profiles.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import bcrypt
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.orm as saorm

from common import utilities
from . import bases
from . import db


class Logins(bases.BaseModel):
    """
    Contains the login information for a Profile in the app. Not every Profile may have an
    associated login. This is not a JSONAPI exposed Model.
    """
    # Not that we should ever delete records, but if the Profile is deleted, delete the Login
    # Also if the email is changed in the Profile, update the Logins.
    email = sa.Column(sa.String(50), sa.ForeignKey('profiles.email', ondelete='CASCADE',
                                                   onupdate='CASCADE'), nullable=False)
    enabled = sa.Column(sa.Boolean, default=True, server_default=sa.text('true'), nullable=False)
    # The hash is really a binary and PostgreSQL cares about that, so use LargeBinary type which
    # results in bytea in PostgreSQL and tinyblob in MySQL. (BTW in python the hash looks like 60
    # chars)
    _password = sa.Column(sa.LargeBinary, nullable=False)

    profile = saorm.relationship('Profiles', back_populates='login')

    @classmethod
    def get_by_email(cls, email):
        """
        Lookup Logins by email address.
        :param str email: email address to lookup
        :return Logins: Matching Login or None
        """
        return db.query(cls).filter(cls.email == email).one_or_none()

    def is_valid_password(self, password):
        """
        Ensure that the provided password is valid.

        We are using this instead of a ``sqlalchemy.types.TypeDecorator`` (which would let us write
        ``User.password == password`` and have the incoming ``password`` be automatically hashed in
        a SQLAlchemy query) because ``compare_digest`` properly compares **all*** the characters of
        the hash even when they do not match in order to avoid timing oracle side-channel attacks.

        :param str password: Password to compare to Login's hash
        :return bool: Password matches
        """
        return bcrypt.checkpw(password.encode('utf8'), self._password)

    @hybrid_property
    def password(self):
        """ Getter so we can use a setter to hash the password before storage. """
        return self._password

    @password.setter
    def password(self, value):
        """
        Ensure that passwords are always stored hashed and salted.
        Requirements: https://blog.codinghorror.com/password-rules-are-bullshit/
        :param str value: New password for login
        """
        if len(value) < 10:
            raise ValueError('Minimum password length is 10 characters.')
        if self.email and value.lower() == self.email.lower():
            raise ValueError('Using email as password forbidden')
        if utilities.is_common_password(value):
            raise ValueError('Commong passwords are forbidden')

        # When a login is first created, give them a salt
        self._password = bcrypt.hashpw(value.encode('utf8'), bcrypt.gensalt())

    @saorm.validates('email')
    def validate_email(self, key, address):  # pylint: disable=unused-argument,no-self-use
        """
        No need to validate email here as it is a foreign key to the validated email in Profiles.
        But we do want to make sure that the password and email don't match.
        :param str key: name of the field to validate.
        :param str address: email address
        :return str: the email address
        :raises ValueError: Invalid email
        """
        if self._password and self.is_valid_password(address):
            raise ValueError('Using email as password forbidden')
        return address
