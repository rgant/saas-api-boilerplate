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


def _add_response_headers(response):
    """
    Modifies the current response to add Global Response Headers.
    :param flask.Response response: Current response to a request.
    :return: Modified response
    :rtype: flask.Response
    """
    # CORS Headers: https://developer.github.com/v3/#cross-origin-resource-sharing
    response_headers = {
        # Headers that are allowed in the COR request:
        'Access-Control-Allow-Headers': 'Authorization, Content-Type, X-Requested-With',
        # Should set these specifically on each request
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE',
        'Access-Control-Allow-Origin': '*',  # Public API, but could also be the web app https://...
        # Response headers that are available to the client code making the COR request:
        # 'Access-Control-Expose-Headers': 'Link, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, X-Poll-Interval',  # pylint: disable=line-too-long
        'Access-Control-Max-Age': '86400',

        # private because most API requests are specific to the requester.
        # max-age 1 minute so we get some caching in cases of multiple requests.
        'Cache-Control': 'private, max-age=60',

        # In DEV environment likely won't have HTTPS. Is that a concern?
        # Could add preload: https://hstspreload.org/
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    response.headers.extend(response_headers)
    return response

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
    return flask.make_response("True", {'Content-Type': 'text/plain'})

def create_api():
    """
    :return: Server for this set of api end points.
    :rtype: flask.Flask
    """
    app = _create_app()
    app.after_request(_add_response_headers)
    app.add_url_rule('/health', 'health_check', _health_check)

    return app
