"""
Tests for the Base API Resource class
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

import pytest
import sqlalchemy as sa

from models import bases
from ourapi import resource
import ourmarshmallow


warnings.simplefilter("error")  # Make All warnings errors while testing.

def test_required_schema():
    """ Resources must have a schema. """
    with pytest.raises(NotImplementedError):
        resource.JsonApiResource()

    class BadResource(resource.JsonApiResource):
        """ Missing the schema parameter """
        pass


    with pytest.raises(NotImplementedError):
        BadResource()

def test_new_resource():
    """ Resources only need a schema. """

    class OkModel(bases.BaseModel):
        """ Model for testing """
        value = sa.Column(sa.String(100), nullable=False)


    class OkModelSchema(ourmarshmallow.Schema):
        """ JSONAPI Schema from SQLAlchemy OkModel. """
        class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
            model = OkModel


    class OkResource(resource.JsonApiResource):
        """ JSONAPI Resource for OkModelSchema endpoints. """
        schema = OkModelSchema

    jsapi_resource = OkResource()
    assert isinstance(jsapi_resource, resource.JsonApiResource)
