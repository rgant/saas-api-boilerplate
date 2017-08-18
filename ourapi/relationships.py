"""
Endpoints for Relationship fields of schema self links.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

from ourmarshmallow.exceptions import IncorrectTypeError, NullPrimaryData
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

    def _get_model(self, model_id):
        """
        Fetch a model by ID, handling common execptions.
        :param int model_id: Id to load from database.
        :return models.bases.BaseModel: Model for id
        :raises exceptions.NotFound: JSONAPI Error Object for missing id.
        """
        the_model = self.relationship.parent_model.get_by_pk(model_id)
        if the_model is None:
            raise exceptions.NotFound({'detail': '{id} not found.'.format(id=model_id),
                                       'source': {'parameter': '/id'}})

        return the_model

    def get(self, model_id):
        """
        Get the relationship data of parent model.
        :param int model_id: Id of parent model to get relationship of.
        :return dict: Either a single Relationship for "to one" relationship, or a collection for
                      "to many".
        :raises exceptions.NotFound: JSONAPI Error Object for missing id.
        """
        the_model = self._get_model(model_id)
        result = self.relationship.serialize(self.relationship.attribute, the_model)
        return result

    def patch(self, model_id, data):
        """
        Set the relationship to the specified values completely. For to many relationships primary
        data must be a list.
        :param int model_id: Id of parent model to get relationship of.
        :param dict data: payload of data to use to update relationship(s).
        :return tuple(None, int): No body, 204 No Content response code.
        :raises exceptions.NotFound: JSONAPI Error Object for missing id.
        """
        the_model = self._get_model(model_id)
        # Relationship Objects should only have id and type fields
        self.relationship.schema.__init__(only=('id', ))

        try:
            related, _ = self.relationship.schema.load(data, many=self.relationship.many)
        except IncorrectTypeError as exc:
            # No clear documentation in the spec for how to handle a type mismatch
            # http://jsonapi.org/format/#crud-updating-relationship-responses
            # So be consistant with updating resources.
            # http://jsonapi.org/format/#crud-updating-responses-409
            raise exceptions.Conflict(exc.messages['errors'][0])
        except NullPrimaryData as exc:
            related = None

        setattr(the_model, self.relationship.attribute, related)
        the_model.save(flush=True)
        return None, 204
