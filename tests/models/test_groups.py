"""
Tests for the Groups Model
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

import pytest
from sqlalchemy.exc import IntegrityError

from models import groups, memberships, profiles


warnings.simplefilter("error")  # Make All warnings errors while testing.

def test_required_fields_blank(dbsession):
    """
    Groups must have a name.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    group = groups.Groups()
    group.save()

    # name is blank
    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_create_group(dbsession):
    """
    Create a Group
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    group = groups.Groups(name='A New Group')
    group.save()
    dbsession.commit()

def test_memberships_relation(dbsession):
    """ Groups can have Memberships relations. """
    profile1 = profiles.Profiles(full_name='92e17a59 740480af51b5', email='6b7d@4c4b.b33d')
    membership1 = memberships.Memberships(profile=profile1)
    profile2 = profiles.Profiles(full_name='0464e813 ddaefbf8d308', email='b377@4a38.a54e')
    membership2 = memberships.Memberships(profile=profile2)
    group = groups.Groups(name='53f8469f-9d33-4fae-be9f-20b47f62ec80')
    group.memberships += (membership1, membership2)

    group.save()
    dbsession.commit()
    assert len(group.memberships) == 2
    assert membership1 in group.memberships
    assert membership2 in group.memberships
