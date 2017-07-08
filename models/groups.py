"""
Groups resource. Collections of Profiles with Memberships in the Group.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import sqlalchemy as sa
import sqlalchemy.orm as saorm

from . import bases

class Groups(bases.BaseModel):
    """ Collection of Profiles for users in the app. """
    name = sa.Column(sa.String(100), nullable=False)

    memberships = saorm.relationship('Memberships', back_populates='group')
