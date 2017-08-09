"""
SQLAlchemy Base Model
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import logging

import sqlalchemy as sa
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql.expression import func as sa_func
from sqlalchemy.util.langhelpers import symbol as sa_symbol

from common import utilities
from . import db


NO_VALUE = sa_symbol('NO_VALUE')

@as_declarative()  # pylint: disable=too-few-public-methods
class Base(object):
    """ Declarative base for ORM. """
    # Don't set timezone=True on DateTime column, the DB should be running as UTC as is the API.
    # This way we don't have to deal with aware datetime objects
    modified_at = sa.Column(sa.DateTime, default=sa_func.now(), nullable=False,
                            onupdate=sa_func.now())
                            # server_default=sa.text('NULL ON UPDATE CURRENT_TIMESTAMP'))  # MySQL

    _cached_tablename = None

    def __repr__(self):
        """
        Custom representation for this Model. Data that isn't currently loaded won't be fetched
        from DB, shows <not loaded> instead.
        Based on:
        https://github.com/kvesteri/sqlalchemy-utils/blob/0.32.14/sqlalchemy_utils/models.py#L41
        Customized to use our __str__ for fully qualified class name.
        :return str: python representation for creating this model.
        """
        state = sa.inspect(self)
        field_reprs = []
        fields = state.mapper.columns.keys()
        for key in fields:
            value = state.attrs[key].loaded_value
            if value == NO_VALUE:
                value = '<not loaded>'
            else:
                value = repr(value)
            field_reprs.append('='.join((key, value)))

        return "{0}({1})".format(self, ', '.join(field_reprs))

    def __str__(self):
        """
        Custom informal string representation with complete model path
        :return str: *fully qualified* name of this model.
        """
        return self.__class__.__module__ + '.' + self.__class__.__name__

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        """
        Convert the TitleCase class names to lower underscore names for the database table name.
        :return str: name for table
        """
        if cls._cached_tablename is None:
            cls._cached_tablename = utilities.camel_to_delimiter_separated(cls.__name__)  # pylint: disable=no-member

        return cls._cached_tablename


class BaseModel(Base):
    """
    Base for all Models. Should not be instantiated directly, but rather subclassed for actual
    models.
    """
    __abstract__ = True
    __versioned__ = {}  # Activate sqlalchemy_continuum versioning for all Resource Models

    id = sa.Column(sa.Integer, primary_key=True)  # pylint: disable=invalid-name

    def delete(self):
        """ Delete this model in the session. Does not flush the session. """
        logger = logging.getLogger(__name__)
        session = db.connect()  # Scoped Session for models.
        session.delete(self)
        logger.info('Deleted %r', self)

    @classmethod
    def _prepare_conditions(cls, conditions):
        """
        Convert a dict of conditions into a list of criterion for a SQL query
        :param dict conditions: List of field names and values to filter a query on
        :return list: filter criterion for a query
        """
        where = []
        for k, v in conditions.items():
            attr = getattr(cls, k)
            if not isinstance(attr.prop, sa.orm.ColumnProperty):
                raise AttributeError('Filtering not supported for relations %s' % k)
            if isinstance(v, list):
                if len(v) > 1:
                    where.append(attr.in_(v))
                    continue
                else:
                    v = v[0]
            where.append(attr == v)
        return where

    @classmethod
    def get_all(cls, conditions=None):
        """
        Lookup all of the records in the table.
        :param dict or None conditions: filter conditions for SQL query
        :return list(BaseModel): Collection of subclass of BaseModel or []
        """
        session = db.connect()  # Scoped Session for models.
        criterion = cls._prepare_conditions(conditions or {})
        return session.query(cls).filter(*criterion).all()

    @classmethod
    def get_by_pk(cls, the_id):
        """
        Lookup record in the table by Primary Key.
        :param int the_id: Primary Key (id) to lookup
        :return BaseModel: Subclass of BaseModel or None
        """
        session = db.connect()  # Scoped Session for models.
        return session.query(cls).filter(cls.id == the_id).one_or_none()

    def save(self, flush=False):
        """
        Add this model to the session. Does not flush the session.
        :param bool flush: Also flush the session after adding model.
        """
        logger = logging.getLogger(__name__)
        session = db.connect()  # Scoped Session for models.
        session.add(self)
        if flush:
            session.flush() # Send INSERT/UPDATE to DB, but don't commit the transaction.
        logger.info('Added %r', self)
