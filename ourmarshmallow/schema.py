"""
Customized Marshmallow-SQLAlchemy and Marshmallow-JSONAPI Schemas to combine Schema Meta data.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import marshmallow as ma
import marshmallow_jsonapi
import marshmallow_sqlalchemy

from common import utilities
from models import db

from .convert import ModelConverter
from .exceptions import MissingIdError, MismatchIdError
from .fields import MetaData


class SchemaOpts(marshmallow_jsonapi.SchemaOpts, marshmallow_sqlalchemy.ModelSchemaOpts):  # pylint: disable=too-few-public-methods
    """ Combine JSON API Schema Opts with SQLAlchemy Schema Opts.
    This fixes the error: AttributeError: 'SchemaOpts' object has no attribute 'model_converter """
    def __init__(self, meta, *args, **kwargs):
        """
        Forces strict=True.
        Forces type_ to kebab-case of self.opts.model.__name__ for JSONAPI recommendation.
        Sets up default self_url and kwargs if model option is set.
        Sets up default self_url_many if model and listable are truthy.
        """
        # Does Resource support a list endpoint? Default False.
        self.listable = getattr(meta, 'listable', False)

        # TODO: ROB 20170726 Check status of github.com/marshmallow-code/marshmallow/issues/377
        # Force strict by default until ticket is resolved.
        meta.strict = True

        # When the base Schema below is first initialized there won't be a model element.
        model = getattr(meta, 'model', None)
        if model:
            # Automatically set the JSONAPI type (marshmallow-jsonapi) based on model name.
            # JSONAPI recommends kebab-case for naming: http://jsonapi.org/recommendations/#naming
            type_ = utilities.camel_to_delimiter_separated(model.__name__, glue='-')
            meta.type_ = type_

            # Self URLs are always based on the JSONAPI type and the model id
            meta.self_url = f'/{type_}/{{id}}'
            meta.self_url_kwargs = {'id': '<id>'}

            # Only include the self_url_many if the Schema declares listable=True
            if getattr(meta, 'listable', False):
                meta.self_url_many = f'/{type_}'

        # Use our custom ModelConverter to turn SQLAlchemy relations into JSONAPI Relationships.
        meta.model_converter = ModelConverter

        def dasherize(text):
            """
            Convert snake_case field names to jsonapi kebab-case.
            :param str text: field name
            :return str: kebab-case name
            """
            return text.replace('_', '-')
        meta.inflect = dasherize

        super().__init__(meta, *args, **kwargs)


class Schema(marshmallow_jsonapi.Schema, marshmallow_sqlalchemy.ModelSchema):
    """ Set custom options class to combine JSONAPI and SQLAlchemy. Set strict option by default.
    Configure DB connection on init. """
    OPTIONS_CLASS = SchemaOpts

    # id must be a string: http://jsonapi.org/format/#document-resource-object-identification
    id = marshmallow_jsonapi.fields.Integer(as_string=True)  # pylint: disable=invalid-name
    # This field is read only, place in meta data: http://jsonapi.org/format/#document-meta
    modified_at = MetaData(marshmallow_jsonapi.fields.DateTime())

    def __init__(self, *args, **kwargs):
        """
        Combine the inits for marshmallow_jsonapi.Schema, marshmallow_sqlalchemy.ModelSchema.
        Forces session=db.connect().
        """
        # Each instance of the schema should have the current session with the DB
        # (marshmallow-sqlschema). This must be done on instance init, not on class creation!
        kwargs['session'] = db.connect()

        super().__init__(*args, **kwargs)

    def unwrap_item(self, item):
        """
        If the schema has an existing instance the id field must be set.
        :raises MissingIdError: id field isn't present when required.
        """
        if self.instance and 'id' not in item:
            raise MissingIdError()

        return super().unwrap_item(item)

    @ma.validates('id')
    def validate_id(self, value):
        """
        If the schema has an existing instance the id value must match id. Use custom errors so we
        can generate to the correct source.pointer and response code.
        :param int value: identifier from payload.
        :raises MismatchIdError: id field doesn't match self.instance.
        """
        if self.instance and self.instance.id != value:
            raise MismatchIdError(actual=value, expected=self.instance.id)
