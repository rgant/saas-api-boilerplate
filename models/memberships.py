"""
Memberships resources. Profiles have Memberships in Groups.
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

class Memberships(bases.BaseModel):
    """ Record of Memberships for Profiles in Groups """
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)
    profile_id = sa.Column(sa.Integer, sa.ForeignKey('profiles.id'), nullable=False)

    group = saorm.relationship('Groups', back_populates='memberships')
    profile = saorm.relationship('Profiles', back_populates='memberships')
