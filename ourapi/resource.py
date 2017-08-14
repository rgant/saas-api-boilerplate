"""
JSONAPI Resources for Flask views.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import flask

from ourmarshmallow.exceptions import IncorrectTypeError, MismatchIdError
from . import base
from . import exceptions


class JsonApiResource(base.BaseJsonApiResource):
    """ Flask MethodView for RESTful API endpoints using a marshmallow-jsonapi schema. """
    schema = None

    def __new__(cls):
        # Inheriting classes must specify schema
        if cls.schema is None:
            raise NotImplementedError("Subclasses must specify the schema for this resource.")

        return super().__new__(cls)

    def _details(self, model_id):
        """
        Read model details by id.
        :param int or None model_id: Id of model
        :return dict: JSONAPI Envelop containing the dumped model as dict.
        """
        the_model, schema = self._get_model(model_id)
        result, _ = schema.dump(the_model)
        return result

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

    def _list(self):
        """
        Read a list of models
        :return list(dict): Collection of JSONAPI Envelops containing the dumped models as dict.
        """
        schema = self.schema(many=True)  # pylint: disable=not-callable
        models_list = schema.opts.model.get_all()
        result, _ = schema.dump(models_list)
        return result

    def delete(self, model_id):
        """
        Delete model by id.
        :param int model_id: Id of model
        :return tuple(None, int): No body, 204 No Content response code.
        """
        the_model, _ = self._get_model(model_id)
        the_model.delete()
        return None, 204

    def get(self, model_id=None):
        """
        For the get method determine if we are listing or fetching a single resource by id.
        :param int or None model_id: Id of model, or None for listing.
        :return: Either _details or _list
        """
        if model_id:
            return self._details(model_id)
        return self._list()

    def patch(self, model_id, data):
        """
        Update a model by id.
        :param int model_id: Id of model
        :param dict data: payload of data to use to update model
        :return dict: JSONAPI Envelop containing the dumped models as dict.
        :raises exceptions.Conflict: id is missing or doesn't match URL.
        """
        the_model, schema = self._get_model(model_id)

        try:
            # Passing existing model instance into load results in extra checks for id in data.
            schema.load(data, instance=the_model)
        except (IncorrectTypeError, MismatchIdError) as exc:
            # http://jsonapi.org/format/#crud-updating-responses-409
            raise exceptions.Conflict(exc.messages['errors'][0])

        the_model.save(flush=True)
        result, _ = schema.dump(the_model)
        return result

    def post(self, data):
        """
        Create a model.
        :param dict data: payload of data to use to create a new model.
        :return tuple(dict, int, dict): New Model Schema dump, 201, Location: URL for Model endpoint
        """
        schema = self.schema()  # pylint: disable=not-callable

        try:
            the_model, _ = schema.load(data)
        except IncorrectTypeError as exc:
            # http://jsonapi.org/format/#crud-creating-responses-409
            raise exceptions.Conflict(exc.messages['errors'][0])

        if the_model.id is not None:
            raise exceptions.Conflict({
                'detail': '`data` object may not include `id` key.',
                'source': {
                    'pointer': '/data/id'
                }
            })

        the_model.save(flush=True)

        result, _ = schema.dump(the_model)
        return result, 201, {'Location': flask.url_for(self.__class__.__name__,
                                                       model_id=the_model.id)}

    @classmethod
    def register(cls, api):
        """
        Add this class as a resource to the flask app/blueprint.
        :param flask.Blueprint or flask.Flask api: API to add this class to as a MethodView.
        """
        view_func = cls.as_view(cls.__name__)

        # Route for Model details by identifier (Read, Update, Delete by identifier)
        # kwargs conversion to flask with int converter. This is a bit ugly.
        # http://flask.pocoo.org/docs/0.12/api/#url-route-registrations
        details_endpoint = cls.schema.opts.self_url.format(id='<int:model_id>')
        api.add_url_rule(details_endpoint, view_func=view_func, methods=('DELETE', 'GET', 'PATCH'))

        # Route for Model Resource without identifier (Create, and possibly Read list)
        methods = ['POST']
        if cls.schema.opts.listable:
            methods.append('GET')
        api.add_url_rule(cls.schema.opts.self_url_many, view_func=view_func, methods=methods)
