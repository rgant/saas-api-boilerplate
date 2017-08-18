"""
Endpoints for Relationship fields of schema related links.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

from . import base
from . import exceptions


class JsonApiRelation(base.BaseJsonApiResource):
    """
    Flask MethodView for RESTful API endpoints using a marshmallow-jsonapi relationship field.
    """
    relation = None

    def __new__(cls):
        # Inheriting classes must specify model and relation field
        if cls.relation is None:
            raise NotImplementedError("Subclasses must specify the relation for this endpoint.")

        return super().__new__(cls)

    def get(self, model_id):
        """
        Get the relation models of parent model.
        :param int model_id: Id of parent model to get relation of.
        :return dict: Either a single BaseModel for "to one" relations, or a collection for
                      "to many".
        :raises exceptions.NotFound: JSONAPI Error Object for missing id.
        """
        the_model = self.relation.parent_model.get_by_pk(model_id)
        if the_model is None:
            raise exceptions.NotFound({'detail': '{id} not found.'.format(id=model_id),
                                       'source': {'parameter': '/id'}})

        related = getattr(the_model, self.relation.attribute)

        # the relation schema @property will magically return an instance of the Schema class.
        result, _ = self.relation.schema.dump(related, many=self.relation.many)
        # TODO: ROB 20170814 Is there a better way to get related resource top level self links?
        result.setdefault('links', {}).update(self=self.relation.get_related_url(the_model))
        return result
