"""
Configuration for py.tests. Does things like setup the database and flask app for individual tests.
https://gist.github.com/alexmic/7857543
"""
import warnings

import pytest

import api
from common import log
import models

warnings.simplefilter("error")  # Make All warnings errors while testing.

# Setup Stream logging for py.test so log messages get output on errors too.
# If something else sets up logging first then this won't trigger.
# For example: db.py calling logging.info() or such.
log.init_logging()

@pytest.fixture(scope='session')
def appclient():
    """
    :return: test client for API app.
    :rtype: flask.testing.FlaskClient
    """
    app = api.create_api()
    client = app.test_client()

    # Helpers for testing API responses
    def validate_response(response, response_code=200, content_type='application/vnd.api+json'):
        """
        Standard checks for any response from the server.
        :param flask.Response response: Response to request from flask test client.
        :param int response_code: Expected response code value.
        :param str content_type: Expected response MIME type (Should be JSONAPI)
        """
        assert response.status_code == response_code

        assert response.headers['Access-Control-Allow-Headers'] == \
            'Authorization, Content-Type, X-Requested-With'
        assert response.headers['Access-Control-Allow-Methods'] == 'GET, POST, PATCH, DELETE'
        assert response.headers['Access-Control-Allow-Origin'] == '*'
        assert response.headers['Access-Control-Max-Age'] == '86400'
        assert response.headers['Cache-Control'] == 'private, max-age=60'
        assert response.headers['Content-Type'] == content_type
        if response_code != 204:
            assert int(response.headers['Content-Length']) > 0
        assert response.headers['Strict-Transport-Security'] == 'max-age=31536000; includeSubDomains'  # pylint: disable=line-too-long
        assert 'Expires' not in response.headers
        assert 'Pragma' not in response.headers
        assert 'Vary' not in response.headers

    client.validate_response = validate_response

    return client

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
    createdb.connect()

    yield createdb

    # This way we can get any database intergrety errors created in testing.
    createdb.flush()

    # Will automatically rollback if not commited in test
    createdb.close()
