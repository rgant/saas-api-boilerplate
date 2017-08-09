"""
HTTP Response Code Exceptions for errors in JSONAPI Requests

* Fetching Data
    * Fetching Resources
        * 200 OK
        * 404 Not Found
    * Fetching Relationships
        * 200 OK
        * 404 Not Found (When parent doesn't exist, but otherwise 200 with null)
    * Inclusion of Related Resources
        * If an endpoint does not support the include parameter, it MUST respond with 400 Bad
        Request to any requests that include it.
        * If a server is unable to identify a relationship path or does not support inclusion of
        resources from a path, it MUST respond with 400 Bad Request.
    * Sparse Fieldsets
    * Sorting
        * If the server does not support sorting as specified in the query parameter sort, it MUST
        return 400 Bad Request.
    * Pagination
    * Filtering
* Creating, Updating and Deleting Resources
    * Creating Resources
        * 201 Created
        * 202 Accepted
        * 204 No Content
        * 403 Forbidden
        * 404 Not Found (when processing a request that references a related resource that does not
        exist.)
        * 409 Conflict (client-generated ID that already exists / type is not among the type(s) that
        constitute the collection represented by the endpoint)
    * Updating Resources
        * 200 OK (changes the resource(s) in ways other than those specified by the request)
        * 202 Accepted
        * 204 No Content (server doesn’t update any attributes besides those provided)
        * 403 Forbidden
        * 404 Not Found
        * 409 Conflict (violate other server-enforced constraints / object’s type and id do not
        match the server’s endpoint)
    * Updating Relationships
        * Updating To-Many Relationships 403 Forbidden response if complete replacement is not
        allowed by the server
        * Deleting Relationships MUST delete the specified members from the relationship or return a
        403 Forbidden response
        * 202 Accepted
        * 204 No Content (update is successful and the representation of the resource in the request
        matches the result)
        * 200 OK (also changes the targeted relationship(s) in other ways than those specified by
        the request)
        * 403 Forbidden
    * Deleting Resources
        * 202 Accepted
        * 204 No Content
        * 200 OK (the server responds with only top-level meta data)
        * 404 Not Found
* Query Parameters
    * If a server encounters a query parameter that does not follow the naming conventions, and the
    server does not know how to process it as a query parameter from this specification, it MUST
    return 400 Bad Request.

JSONAPI uses http://tools.ietf.org/html/rfc7231 so base error class should be 400 Bad Request
http://jsonapi.org/format/#fetching-resources-responses-other
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
try:
    from builtins import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
except ImportError:
    import sys
    print("WARNING: Cannot Load builtins for py3 compatibility.", file=sys.stderr)

import werkzeug.exceptions


class JSONAPIError(werkzeug.exceptions.HTTPException):
    """ Base class for all exceptions in this module. """

    def get_body(self):
        """ Generate a JSONAPI Error Object Response. """
        err = {'status': str(self.code), 'title': self.name}
        if isinstance(self.description, str):
            err['detail'] = self.description
        else:
            err.update(self.description)
        return {'errors': [err]}

    def get_headers(self):  # pylint: disable=no-self-use
        """ Use the JSONAPI MIME type for error responses."""
        return [('Content-Type', 'application/vnd.api+json')]


class BadRequest(JSONAPIError, werkzeug.exceptions.BadRequest):
    """ 400 Bad Request: General request errors as per rfc7231. """
    pass


class Forbidden(JSONAPIError, werkzeug.exceptions.Forbidden):
    """ 403 Forbidden: unsupported request to create, update, delete resource or relationship. """
    pass


class NotFound(JSONAPIError, werkzeug.exceptions.NotFound):
    """ 404 Not Found: Resource doesn't exist. """
    pass


class Conflict(JSONAPIError, werkzeug.exceptions.Conflict):
    """ 409 Conflict: fails server unique constraint or id issues. """
    pass
