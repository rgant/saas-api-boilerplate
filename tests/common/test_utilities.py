"""
Tests for common utility functions
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import warnings

from common import utilities


warnings.simplefilter("error")  # Make All warnings errors while testing.


def test_camel_to_snake_case():
    """ Should convert Class Names to Database Table names. """
    test_strings = {
        'test': 'test',
        'Test': 'test',
        'TEST': 'test',
        # https://stackoverflow.com/a/1176023
        'CamelCase': 'camel_case',
        'CamelCamelCase': 'camel_camel_case',
        'Camel2Camel2Case': 'camel2_camel2_case',
        'getHTTPResponseCode': 'get_http_response_code',
        'get2HTTPResponseCode': 'get2_http_response_code',
        'HTTPResponseCode': 'http_response_code',
        'HTTPResponseCodeXYZ': 'http_response_code_xyz',
        # https://gist.github.com/jaytaylor/3660565
        'snakesOnAPlane': 'snakes_on_a_plane',
        'SnakesOnAPlane': 'snakes_on_a_plane',
        'snakes_on_a_plane': 'snakes_on_a_plane',
        'IPhoneHysteria': 'i_phone_hysteria',
        'iPhoneHysteria': 'i_phone_hysteria',
        # These strings aren't camel case so it should do something weird:
        '_Test': '__test',
        '_test_Method': '_test__method',
        '__test__Method': '__test___method',
        '__CamelCase': '___camel_case',
        '_Camel_Case': '__camel__case',
        # This one might want a fix some day, but it is also bad camel case:
        'getHTTPresponseCode': 'get_htt_presponse_code'
    }

    for camel, snake in test_strings.items():
        assert utilities.camel_to_delimiter_separated(camel) == snake

def test_camel_to_kebab_case():
    """ camel_to_delimiter_separated also takes a glue parameter to allow for kebab-case. """
    assert utilities.camel_to_delimiter_separated('Camel2Camel2Case', glue='-') == \
        'camel2-camel2-case'

def test_is_common_password():
    """ Detect common passwords. """
    assert utilities.is_common_password('password')
    assert utilities.is_common_password('Password')
    assert utilities.is_common_password('PASSWORD')
    assert not utilities.is_common_password('foobar')

def test_validate_email():
    """ Tests email validation function vs list of good and bad emails addresses. """
    # http://blogs.msdn.com/b/testing123/archive/2009/02/05/email-address-test-cases.aspx
    good_addresses = ['email@domain.com',  # Valid email
                      'firstname.lastname@domain.com',  # Email contains dot in the address field
                      'email@subdomain.domain.com',  # Email contains dot with subdomain
                      'firstname+lastname@domain.com',  # Plus sign is considered valid character
                      '"email"@domain.com',  # Quotes around email is considered valid
                      "o'brian@domain.com",  # Single quotes in email is considered valid
                      '1234567890@domain.com',  # Digits in address are valid
                      'email@domain-one.com',  # Dash in domain name is valid
                      '_______@domain.com',  # Underscore in the address field is valid
                      'email@domain.name',  # .name is valid Top Level Domain name
                      'email@domain.co.jp',  # Dot in Top Level Domain name also considered valid
                      'あいうえお@domain.com',  # Unicode char as address
                      'firstname-lastname@domain.com']  # Dash in address field is valid
    for addr in good_addresses:
        assert utilities.is_valid_email_address(addr)

    bad_addresses = ['plainaddress',  # Missing @ sign and domain
                     '#@%^%#$@#$@#.com',  # Garbage
                     '@domain.com',  # Missing username
                     'email @domain.com',  # Space
                     'e mail@domain.com',  # Space
                     ' email@domain.com',  # Space
                     'Joe Smith <email@domain.com>',  # Encoded html within email is invalid
                     'email@domain.com (Joe Smith)'  # Text followed email is not allowed
                     'email.domain.com',  # Missing @
                     'email@domain@domain.com',  # Two @ sign
                     'email@domain',  # Missing top level domain (.com/.net/.org/etc)
                     'email@domain..com']  # Multiple dot in the domain portion is invalid
    for addr in bad_addresses:
        assert not utilities.is_valid_email_address(addr)

    # These might not be valid, but we aren't catching them right now.
    fail_addresses = ['.email@domain.com',  # Leading dot in address is not allowed
                      'email.@domain.com',  # Trailing dot in address is not allowed
                      'email..email@domain.com',  # Multiple dots in username
                      'email@-domain.com']  # Leading dash in front of domain is invalid
    for addr in fail_addresses:
        assert utilities.is_valid_email_address(addr)
