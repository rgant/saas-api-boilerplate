"""
Database connection for models
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import logging
import os

import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session


CONNECTIONS = {
    'dev': 'postgresql://api@localhost/saas_dev',
    # 'dev': 'mysql+pymysql://root@localhost/saas_dev?charset=utf8mb4',
    'stage': 'postgresql://api@localhost/saas_stage',
    'prod': 'postgresql://api@localhost/saas_prod'
}
ENV = os.environ.get('ENV', 'dev')

# Needed for BaseModel.metadata.create_all(ENGINE)
ENGINE = sqlalchemy.create_engine(CONNECTIONS[ENV])

def _init():
    """
    Initalize the FACTORY constant
    :return sqlalchemy.orm.scoped_session: contextual/thread local session factory.
    """
    factory = scoped_session(sessionmaker(bind=ENGINE))
    env_name = {'dev': '\033[0;32mDEV\033[0m',
                'stage': '\033[1;33mSTAGE\033[0m',
                'prod': '\033[4;31mPROD\033[0m'}.get(ENV)

    logger = logging.getLogger(__name__)
    logger.debug('Connected to %s database.', env_name)
    return factory

FACTORY = _init()

def close():
    """ Dispose of the current session. """
    logger = logging.getLogger(__name__)
    logger.debug('Remove Scoped Session.')
    FACTORY.remove()

def commit():
    """ Apply the current session to DB. This will populate the IDs and other defaults. """
    logger = logging.getLogger(__name__)
    logger.debug('Commit Session.')
    FACTORY.commit()  # pylint: disable=no-member

def connect():
    """
    New/current session for context/thread.
    :retrun sqlalchemy.orm.session.Session: persistence operations for ORM-mapped objects
    """
    session = FACTORY()
    logger = logging.getLogger(__name__)
    logger.debug('Return Scoped Session: %r.', session)
    return session

def rollback():
    """ Rollback the current session from DB. """
    logger = logging.getLogger(__name__)
    logger.debug('Rollback Session.')
    FACTORY.rollback()  # pylint: disable=no-member
