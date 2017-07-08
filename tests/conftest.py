"""
Configuration for py.tests. Does things like setup the database and flask app for individual tests.
https://gist.github.com/alexmic/7857543
"""
import warnings

import pytest

from common import log
import models

warnings.simplefilter("error")  # Make All warnings errors while testing.

# Setup Stream logging for py.test so log messages get output on errors too.
# If something else sets up logging first then this won't trigger.
# For example: db.py calling logging.info() or such.
log.init_logging()

@pytest.fixture(scope='session')
def createdb():
    """
    Session-wide test database.
    :yield models.db: database module for models
    """
    models.__create_tables()  # pylint: disable=protected-access

    yield models.db

    models.__drop_tables()  # pylint: disable=protected-access


@pytest.fixture(scope='function')
def dbsession(createdb):  # pylint: disable=redefined-outer-name
    """
    Create a new session for a test, afterwards flush, rollback and then close the session.
    :param createdb: pytest fixture to create the test tables and delete them when test is done.
    :yield sqlalchemy.orm.session.Session: sqlalchemy session for test
    """
    session = createdb.connect()

    yield session

    # This way we can get any database intergrety errors created in testing.
    session.flush()

    createdb.rollback()
    createdb.close()
