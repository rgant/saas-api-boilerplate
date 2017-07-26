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


class SchemaOpts(marshmallow_jsonapi.SchemaOpts, marshmallow_sqlalchemy.ModelSchemaOpts):  # pylint: disable=too-few-public-methods
    """ Combine JSON API Schema Opts with SQLAlchemy Schema Opts.
    This fixes the error: AttributeError: 'SchemaOpts' object has no attribute 'model_converter """
    pass

class Schema(marshmallow_jsonapi.Schema, marshmallow_sqlalchemy.ModelSchema):
    """ Set custom options class to combine JSONAPI and SQLAlchemy. Set strict option by default.
    Configure DB connection on init. """
    OPTIONS_CLASS = SchemaOpts

    def __init__(self, *args, **kwargs):
        """
        Each instance of the schema should have the current session with the DB
        (marshmallow-sqlschema).
        """
        # Force strict by default until https://github.com/marshmallow-code/marshmallow/issues/377
        # TODO: ROB 20170726 Check status of marshmallow-code/marshmallow/issues/377
        if 'strict' not in kwargs:
            kwargs['strict'] = True

        kwargs['session'] = db.connect()

        # Automatically set the JSONAPI type based on model name
        if not self.opts.type_ and self.opts.model:
            # JSONAPI recommends kabobcase for naming: http://jsonapi.org/recommendations/#naming
            self.opts.type_ = utilities.camel_to_snake_case(self.opts.model.__name__, glue='-')

        super().__init__(*args, **kwargs)
