"""
Customized Marshmallow-SQLAlchemy and Marshmallow-JSONAPI Schemas to combine Meta data.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import marshmallow_jsonapi
import marshmallow_sqlalchemy

from common import utilities
from models import db

from .fields import MetaData

class SchemaOpts(marshmallow_jsonapi.SchemaOpts, marshmallow_sqlalchemy.ModelSchemaOpts):  # pylint: disable=too-few-public-methods
    """ Combine JSON API Schema Opts with SQLAlchemy Schema Opts.
    This fixes the error: AttributeError: 'SchemaOpts' object has no attribute 'model_converter """
    pass


class Schema(marshmallow_jsonapi.Schema, marshmallow_sqlalchemy.ModelSchema):
    """ Set custom options class to combine JSONAPI and SQLAlchemy. Set strict option by default.
    Configure DB connection on init. """
    OPTIONS_CLASS = SchemaOpts

    modified_at = MetaData(marshmallow_jsonapi.fields.DateTime())

    def __init__(self, *args, **kwargs):
        """
        Combine the inits for marshmallow_jsonapi.Schema, marshmallow_sqlalchemy.ModelSchema.
        Forces strict=True.
        Forces session=db.connect().
        Forces self.opts.type_ to kebab-case of self.opts.model.__name__ for JSONAPI recommendation.
        """
        # TODO: ROB 20170726 Check status of github.com/marshmallow-code/marshmallow/issues/377
        # Force strict by default until ticket is resolved.
        kwargs['strict'] = True

        # Each instance of the schema should have the current session with the DB
        # (marshmallow-sqlschema).
        kwargs['session'] = db.connect()

        # Automatically set the JSONAPI opts.type_ (marshmallow-jsonapi) based on model name.
        # JSONAPI recommends kebab-case for naming: http://jsonapi.org/recommendations/#naming
        self.opts.type_ = utilities.camel_to_delimiter_separated(self.opts.model.__name__, glue='-')

        super().__init__(*args, **kwargs)
