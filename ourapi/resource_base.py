"""
JSONAPI Resources for Flask views.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import flask.views


class Resource(flask.views.MethodView):
    """ Flask MethodView for RESTful API end points using a marshmallow-jsonapi schema. """
    schema = None
    endpoint = None

    def __new__(cls):
        try:
            assert cls.schema is not None    # Inheriting classes must specify
        except AssertionError:
            raise NotImplementedError("Subclasses must specify the schema for this endpoint.")
        return super().__new__(cls)

    @classmethod
    def register(cls, api):
        """
        Add this class as a resource to the flask app/blueprint.
        :param flask.Blueprint or flask.Flask api: API to add this class to as a MethodView.
        """
        api.add_url_rule(cls.endpoint, view_func=cls.as_view(cls.__name__))
