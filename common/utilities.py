"""
Utilities functions used generally by the project.
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import re

from . import common_passwords


def camel_to_snake_case(name, glue='_'):
    """
    Convert CamelCase to snake_case.
    :param str name: CamelCase name to convert
    :return str: snake_case version of name
    """
    # From https://stackoverflow.com/a/1176023
    first_cap_re = re.compile('(.)([A-Z][a-z]+)')
    all_cap_re = re.compile('([a-z0-9])([A-Z])')
    replacement = r'\1{glue}\2'.format(glue=glue)
    ex = first_cap_re.sub(replacement, name)
    return all_cap_re.sub(replacement, ex).lower()

def is_valid_email_address(address):
    """
    Check if the given email address appears valid.
    :param str address: Email Address to test
    :return bool: If it looks like a valid email address.
    """
    # From http://stackoverflow.com/questions/8022530/python-check-for-valid-email-address
    valid_email_address_pattern = re.compile(r'^[^@ ]+@[^@. ]+(?:\.[^@. ]+)+$')
    return bool(valid_email_address_pattern.match(address))

def is_common_password(passwd):
    """
    Check passwd against a list of common passwords.
    :param str passwd: Password to test
    :return bool: Password is common
    """
    return passwd.lower() in common_passwords.COMMON_PASSWORDS
