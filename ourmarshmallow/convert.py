"""
Customized Marshmallow-SQLAlchemy ModelConverter to combine Related and Relationship fields.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import marshmallow_sqlalchemy

from common import utilities

from .fields import Relationship


class ModelConverter(marshmallow_sqlalchemy.ModelConverter):
    """ Customize SQLAlchemy Model Converter to use JSON API Relationships. """

    def _get_field_class_for_property(self, prop):
        """ Use our Relationship field type for SQLAlchemy relations instead. """
        if hasattr(prop, 'direction'):
            return Relationship
        return super()._get_field_class_for_property(prop)

    def _add_relationship_kwargs(self, kwargs, prop):
        """ Customize the kwargs for Relationship field based on prop. """
        super()._add_relationship_kwargs(kwargs, prop)

        # All Schema names should be based on Model name.
        kwargs['schema'] = prop.mapper.class_.__name__ + 'Schema'
        # If the relation uses a list then the Relationship is many
        kwargs['many'] = prop.uselist
        # JSONAPI type is calculated from Model name to kebab-case.
        kwargs['type_'] = utilities.camel_to_delimiter_separated(prop.mapper.class_.__name__,
                                                                 glue='-')
        # The relationship's URLs will be calculated from the parent schema's self URL.
        kwargs['parent_self_url'] = self.schema_cls.opts.self_url
        # Relationship URLs will use the same kwargs as the parent schema.
        kwargs['self_url_kwargs'] = self.schema_cls.opts.self_url_kwargs
