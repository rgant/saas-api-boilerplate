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

from . import bases
from . import db


class Logins(bases.BaseModel):
    """
    Contains the login information for a Profile in the app. Not every Profile may have an
    associated login. This is not a JSONAPI exposed Model.
    """
    email = sa.Column(sa.String(50), sa.ForeignKey('profiles.email', ondelete='CASCADE'),
                      nullable=False)
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
        session = db.connect()  # Scoped Session for models.
        print(cls.email, email)
        return session.query(cls).filter(cls.email == email).one_or_none()

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
        :param str value: New password for login
        """
        # When a login is first created, give them a salt
        self._password = bcrypt.hashpw(value.encode('utf8'), bcrypt.gensalt())

    # @saorm.validates('email')
    # No need to validate email here as it is a foreign key to the validated email in Profiles
