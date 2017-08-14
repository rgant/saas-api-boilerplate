"""
Endpoints for Relationship fields of schema self links.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

from . import base
from . import exceptions


class JsonApiRelationship(base.BaseJsonApiResource):
    """
    Flask MethodView for RESTful API endpoints using a marshmallow-jsonapi relationship field.
    """
    relationship = None

    def __new__(cls):
        # Inheriting classes must specify model and relationship field
        if cls.relationship is None:
            raise NotImplementedError("Subclasses must specify the relationship for this endpoint.")
        else:
            cls.relationship.include_resource_linkage = True

        return super().__new__(cls)

    def get(self, model_id):
        """
        Get the relationship data of parent model.
        :param int model_id: Id of parent model to get relationship of.
        :return dict: Either a single Relationship for "to one" relationship, or a collection for
                      "to many".
        """
        the_model = self.relationship.parent_model.get_by_pk(model_id)
        if the_model is None:
            raise exceptions.NotFound({'detail': '{id} not found.'.format(id=model_id),
                                       'source': {'parameter': '/id'}})

        try:
            result = self.relationship.serialize(self.relationship.attribute, the_model)
        except AttributeError:
            raise exceptions.NotFound({'detail': 'Relationship relation "{attribute}" not found.'\
                                       .format(attribute=self.relationship.attribute),
                                       'source': {'parameter': '/relation'}})

        return result
