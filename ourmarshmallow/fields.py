"""
Customized Fields for Our Marshmallow.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

from marshmallow.base import FieldABC
# Make marshmallow core and jsonapi fields importable from ourmarshmallow
from marshmallow.fields import *  # pylint: disable=wildcard-import,unused-wildcard-import
import marshmallow_jsonapi.fields
import marshmallow_sqlalchemy.fields


class MetaData(marshmallow_jsonapi.fields.Meta):
    """ Per-field metadata wrapper. Turns another field into MetaData.
    Based on marshmallow.fields.List """
    def __init__(self, cls_or_instance, **kwargs):
        # Force dump_only=True.
        kwargs['dump_only'] = True
        # Since we don't always know what the attribute is for this field, and Meta sets the
        # load_from to '_meta' it is difficult to load this value so don't.

        super().__init__(**kwargs)

        if isinstance(cls_or_instance, type):
            if not issubclass(cls_or_instance, FieldABC):
                raise ValueError('The type of the metadata elements must be a subclass of '
                                 'marshmallow.base.FieldABC')
            self.container = cls_or_instance()
        else:
            if not isinstance(cls_or_instance, FieldABC):
                raise ValueError('The instances of the metadata elements must be of type '
                                 'marshmallow.base.FieldABC')
            self.container = cls_or_instance

    def _serialize(self, value, attr, obj):  # pylint: disable=arguments-differ
        return {self.dump_to or attr: self.container._serialize(value, attr, obj)}  # pylint: disable=protected-access


class Relationship(marshmallow_jsonapi.fields.Relationship, marshmallow_sqlalchemy.fields.Related):
    """
    Combine the marshmallow-jsonapi.fields.Relationship with marshmallow-sqlalchemy.fields.Related.
    """
    def __init__(self, parent_self_url='', relationship_name='', parent_model=None, **kwargs):
        """
        :param str parent_self_url: Used to calculate self_url and related_url from a parent schema.
        :param str relationship_name: Name of this relationship for self_url and related_url.
        :param models.bases.BaseModel parent_model: Model Class of Schema containing this field.
        """
        # Calculate our relationship URLs beased on the parent schema's self_url
        if parent_self_url and relationship_name and kwargs['self_url_kwargs']:
            kwargs['self_url'] = '{0}/relationships/{1}'.format(parent_self_url, relationship_name)
            kwargs['related_url'] = '{0}/{1}'.format(parent_self_url, relationship_name)
            kwargs['related_url_kwargs'] = kwargs['self_url_kwargs']

        # Set the class of the model for the schema containing this field.
        self.parent_model = parent_model

        super().__init__(**kwargs)
