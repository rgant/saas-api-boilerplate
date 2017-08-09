"""
JSONAPI List Resource.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import flask

from ourmarshmallow.exceptions import IncorrectTypeError, MismatchIdError
from . import exceptions
from . import resource_base


class ResourceDetail(resource_base.Resource):
    """ End points to Read, Update, and Delete a specific Model by id. """
    def __new__(cls):
        cls = super().__new__(cls)
        cls.endpoint = cls.schema.opts.self_url
        return cls

    def _get_model(self, model_id):
        """
        Fetch a model by ID, handling common execptions.
        :param int model_id: Id to load from database.
        :return tuple(BaseModel, Schema): Model for id, Schema for Model
        :raises exceptions.NotFound: JSONAPI Error Object for missing id.
        """
        schema = self.schema()  # pylint: disable=not-callable
        the_model = schema.opts.model.get_by_pk(model_id)
        if the_model is None:
            raise exceptions.NotFound({'detail': '{id} not found.'.format(id=model_id),
                                       'source': {'parameter': '/id'}})

        return the_model, schema

    def delete(self, model_id):
        """
        Delete model by id.
        :param int model_id: Id of model
        :return tuple(None, int): No body, 204 No Content
        """
        the_model, _ = self._get_model(model_id)
        the_model.delete()
        return None, 204

    def get(self, model_id):
        """
        Read model details by id.
        :param int model_id: Id of model
        :return dict: JSONAPI Envelop containing the dumped models as dict.
        """
        the_model, schema = self._get_model(model_id)
        result, _ = schema.dump(the_model)
        return result

    def patch(self, model_id):
        """
        Update a model by id.
        :param int model_id: Id of model
        :return dict: JSONAPI Envelop containing the dumped models as dict.
        :raises exceptions.Conflict: id is missing or doesn't match URL.
        """
        the_model, schema = self._get_model(model_id)

        try:
            # Passing existing model instance into load results in extra checks for id in data.
            schema.load(flask.request.get_json(force=True), instance=the_model)
        except (IncorrectTypeError, MismatchIdError) as exc:
            # http://jsonapi.org/format/#crud-updating-responses-409
            raise exceptions.Conflict(exc.messages['errors'][0])

        the_model.save()
        result, _ = schema.dump(the_model)
        return result
