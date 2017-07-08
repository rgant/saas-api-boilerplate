"""
Tests for the Memberships Model
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

def test_required_relations(dbsession):
    """
    Memberships must have a Profile and a Group.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    inst = memberships.Memberships()
    inst.save()

    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_profile_missing(dbsession):
    """
    Membership Profile not existing is an error.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    group = groups.Groups(name='61f7d724-d90c-4e2f-85f4-7cab51d68b61')
    membership = memberships.Memberships(group=group)
    membership.save()

    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_group_missing(dbsession):
    """
    Membership Group not existing is an error.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    profile = profiles.Profiles(full_name='103ae318 69f4f2471acc', email='73c5@4568.8dd9')
    membership = memberships.Memberships(profile=profile)
    membership.save()

    with pytest.raises(IntegrityError):
        dbsession.commit()

def test_required_fields(dbsession):
    """
    Membership Profile and Group are required fields.
    :param sqlalchemy.orm.session.Session dbsession: pytest fixture for database session
    """
    group = groups.Groups(name='82cc113d-fee2-4b85-b28e-2bf312bec470')
    profile = profiles.Profiles(full_name='b0596fbf b3b53ea6a099', email='7b27@4c2b.a396')
    membership = memberships.Memberships(group=group, profile=profile)
    membership.save()
    dbsession.commit()
