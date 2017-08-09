"""
Tests for our customized marshmallow-sqlalchemy converter to support JSONAPI Relationship fields.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

import sqlalchemy as sa
import sqlalchemy.orm as saorm

from models import bases
import ourmarshmallow


warnings.simplefilter("error")  # Make All warnings errors while testing.

class Nodes(bases.BaseModel):
    """ Model for testing relationship conversion. """
    value = sa.Column(sa.String(100), nullable=False)

    parent_id = sa.Column(sa.Integer(), sa.ForeignKey('nodes.id'))

    parent = saorm.relationship('Nodes', back_populates='children', remote_side='Nodes.id')
    children = saorm.relationship('Nodes', back_populates='parent')

class NodesSchema(ourmarshmallow.Schema):
    """ Schema for testing relationship conversion. """
    class Meta(object):  # pylint: disable=missing-docstring,too-few-public-methods
        model = Nodes


def test_get_field_class():
    """ SQLAlchemy relations should return ourmarshmallow Relationship field. """
    converter = ourmarshmallow.convert.ModelConverter(schema_cls=NodesSchema)

    assert issubclass(converter._get_field_class_for_property(Nodes.parent.property),  # pylint: disable=protected-access
                      ourmarshmallow.fields.Relationship)
    assert issubclass(converter._get_field_class_for_property(Nodes.children.property),  # pylint: disable=protected-access
                      ourmarshmallow.fields.Relationship)

    assert issubclass(converter._get_field_class_for_property(Nodes.id.property),  # pylint: disable=protected-access
                      ourmarshmallow.fields.Integer)
    assert issubclass(converter._get_field_class_for_property(Nodes.modified_at.property),  # pylint: disable=protected-access
                      ourmarshmallow.fields.DateTime)
    assert issubclass(converter._get_field_class_for_property(Nodes.value.property),  # pylint: disable=protected-access
                      ourmarshmallow.fields.String)

def test_relationship_kwargs():
    """ Confirm correct defaults are set on Relation properties. """
    converter = ourmarshmallow.convert.ModelConverter(schema_cls=NodesSchema)
    kwargs = {}
    converter._add_relationship_kwargs(kwargs, Nodes.parent.prop)  # pylint: disable=protected-access
    assert kwargs['schema'] == 'NodesSchema'
    assert kwargs['many'] is False
    assert kwargs['type_'] == 'nodes'
    assert kwargs['attribute'] == 'parent'
    assert kwargs['relationship_name'] == 'parent'
    assert kwargs['parent_self_url'] == NodesSchema.opts.self_url
    assert kwargs['self_url_kwargs'] == NodesSchema.opts.self_url_kwargs

def test_many_relationship_kwargs():
    """ Confirm correct defaults are set on Relation properties for to many relations. """
    converter = ourmarshmallow.convert.ModelConverter(schema_cls=NodesSchema)
    kwargs = {}
    converter._add_relationship_kwargs(kwargs, Nodes.children.prop)  # pylint: disable=protected-access
    assert kwargs['schema'] == 'NodesSchema'
    assert kwargs['many'] is True
    assert kwargs['type_'] == 'nodes'
    assert kwargs['attribute'] == 'children'
    assert kwargs['relationship_name'] == 'children'
    assert kwargs['parent_self_url'] == NodesSchema.opts.self_url
    assert kwargs['self_url_kwargs'] == NodesSchema.opts.self_url_kwargs

def test_manytomany_relations():
    """ All DIRECTION_MAPPING should be False, and property2field should return a Relationship for
    list relations. """
    for _, is_many in ourmarshmallow.convert.ModelConverter.DIRECTION_MAPPING.items():
        assert is_many is False

    # marshmallow-sqlalchemy.convert turns directional properties into Lists, but we want to use
    # our Relationship fields.
    converter = ourmarshmallow.convert.ModelConverter(schema_cls=NodesSchema)
    assert Nodes.children.prop.uselist is True
    assert Nodes.children.prop.direction.name == 'ONETOMANY'
    field = converter.property2field(Nodes.children.prop)
    assert isinstance(field, ourmarshmallow.fields.Relationship)
