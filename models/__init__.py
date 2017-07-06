"""
Resource Models for API and database tables.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

from sqlalchemy_continuum import make_versioned


def __create_tables():
    """
    Create the tables for our models. Manual use or testing

    Example Usage:
    $ ENV=stage python
    >>> import sqmodels
    INFO:db:_init:36:Connected to STAGE database.
    >>> sqmodels.__create_tables()
    """
    from . import db
    from . import bases
    make_versioned(user_cls=None)
    bases.Base.metadata.create_all(db.ENGINE)  # pylint: disable=no-member

def __drop_tables():
    """ Drop the tables for our models. For testing only. """
    from . import db
    from . import bases
    bases.Base.metadata.drop_all(db.ENGINE)  # pylint: disable=no-member
