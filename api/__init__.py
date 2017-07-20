"""
JSONAPI Spec implementation of API for models.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import flask
from werkzeug.contrib.fixers import ProxyFix


def _create_app():
    """
    Flask Application factory.
    :return: Flask app for an API.
    :rtype: flask.Flask
    """
    app = flask.Flask(__name__)
    # http://werkzeug.pocoo.org/docs/0.12/contrib/fixers/#werkzeug.contrib.fixers.ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app

def _health_check():
    """ Responds with True if the App is nominally handling requests """
    return "True"

def create_api():
    """
    :return: Server for this set of api end points.
    :rtype: flask.Flask
    """
    app = _create_app()
    app.add_url_rule('/health', 'health_check', _health_check)

    return app
