"""
Tests for our customized marshmallow Fields
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

import ourmarshmallow.fields


warnings.simplefilter("error")  # Make All warnings errors while testing.

def test_metadata_container_class():
    """ Can create a MetaData field using a field Class. """
    field = ourmarshmallow.fields.MetaData(ourmarshmallow.fields.Str)
    assert isinstance(field.container, ourmarshmallow.fields.Str)

def test_metadata_container_inst():
    """ Can create a MetaData field using a field Class. """
    field = ourmarshmallow.fields.MetaData(ourmarshmallow.fields.Str())
    assert isinstance(field.container, ourmarshmallow.fields.Str)

def test_metadata_dump_only():
    """ Because of issues deserializing from meta these fields are always dump_only. """
    field = ourmarshmallow.fields.MetaData(ourmarshmallow.fields.Str)
    assert field.dump_only is True

def test_metadata_serialize():
    """ Should be able to serialize value via container field. """
    field = ourmarshmallow.fields.MetaData(ourmarshmallow.fields.Int)
    result = field.serialize('offset', {'offset': 1})
    assert result == {'offset': 1}

def test_metadata_dump_to():
    """ Should be able to dump_to another field name. """
    field = ourmarshmallow.fields.MetaData(ourmarshmallow.fields.Int, dump_to='page')
    result = field.serialize('offset', {'offset': 1})
    assert result == {'page': 1}

def test_relationship_defaults():
    """ Automatically set self_url and related_url based on parent url and relationship name. """
    field = ourmarshmallow.fields.Relationship(parent_self_url='/foo/bar', relationship_name='baz',
                                               self_url_kwargs={'quz': 'corge'})
    assert field.self_url == '/foo/bar/relationships/baz'
    assert field.related_url == '/foo/bar/baz'
    assert field.related_url_kwargs == {'quz': 'corge'}

def test_relationship_parent_model():
    """ Relationship should know it's parent model class. """
    class AModel(object):  # pylint: disable=too-few-public-methods
        """ Dummy model for testing. """
        pass

    field = ourmarshmallow.fields.Relationship(parent_model=AModel)
    assert field.parent_model == AModel
