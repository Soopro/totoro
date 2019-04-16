# coding=utf-8
from __future__ import absolute_import

import httplib


# base
class APIError(Exception):
    """
    Base class for all api exceptions.
    Subclasses should provide properties:
    - `status_code`
    - `status_message`
    - `message`
    - `response_code`
    """

    status_code = httplib.INTERNAL_SERVER_ERROR
    response_code = 0
    status_message = 'api_error'

    def __init__(self, error=None):
        message = None
        if isinstance(error, Exception):
            if hasattr(error, 'message'):
                message = unicode(error.message)
            if hasattr(error, 'status_code'):
                self.status_code = error.status_code
            if hasattr(error, 'response_code'):
                self.response_code = error.response_code
            if hasattr(error, 'status_message'):
                self.status_message = error.status_message
        elif isinstance(error, basestring):
            message = unicode(error)
        super(APIError, self).__init__(message)

    def __str__(self):
        if self.message:
            return u'{}: {}'.format(self.status_message, self.message)
        else:
            return self.status_message


class APIResponse(object):
    status_code = 200
    response_code = 0
    data = {}

    def __init__(self, data, status_code=200, response_code=0):
        self.status_code = 200
        self.response_code = 0
        self.data = data

    def __str__(self):
        return u'{} {}'.format(self.status_code, self.response_code)


# not found
class NotFound(APIError):
    status_code = httplib.NOT_FOUND
    status_message = 'RESOURCE_NOT_FOUND'
    response_code = 100000


# forbidden
class PermissionDenied(APIError):
    status_code = httplib.FORBIDDEN
    status_message = 'FORBIDDEN'
    response_code = 101000


class PermissionExpired(PermissionDenied):
    status_message = 'EXPIRED'
    response_code = 101001


# unauthorized
class Unauthorized(APIError):
    status_code = httplib.UNAUTHORIZED
    status_message = 'UNAUTHORIZED'
    response_code = 102000


# not allow
class MethodNotAllowed(APIError):
    status_code = httplib.METHOD_NOT_ALLOWED
    status_message = 'REQUEST_METHOD_NOT_ALLOWED'
    response_code = 103000


# bad request
class BadRequest(APIError):
    status_code = httplib.BAD_REQUEST
    status_message = 'BAD_REQUEST'
    response_code = 104000


class RequestSourceNotExists(BadRequest):
    response_code = 104010
    status_message = 'REQUEST_SOURCE_NOT_EXISTS'


class InvalidRequest(BadRequest):
    response_code = 104020
    status_message = 'INVALID_REQUEST'


class ParameterRequired(BadRequest):
    response_code = 104030
    status_message = 'PARAMETER_REQUIRED'


class RequestMaxLimited(BadRequest):
    response_code = 104040
    status_message = 'REQUEST_REACHES_MAX_LIMIT'


# internal server error
class InternalServerError(APIError):
    status_code = httplib.INTERNAL_SERVER_ERROR
    response_code = 105000
    status_message = 'INTERNAL_SERVER_ERROR'


class ResponseInstanceTypeError(InternalServerError):
    response_code = 105010
    status_message = 'API_RESPONSE_TYPE_ERROR'


class UncaughtException(InternalServerError):
    response_code = 105020
    status_message = 'UNCAUGHT_EXCEPTION'


class MongoDBError(InternalServerError):
    response_code = 105030
    status_message = 'MONGODB_ERROR'


class RenderingError(InternalServerError):
    status_code = 105040
    status_message = 'RENDERING_ERROR'


# conflict
class ConflictError(APIError):
    status_code = httplib.CONFLICT
    status_message = 'CONFLICT_ERROR'
    response_code = 106000


# unexpection
class Unexpected(APIError):
    status_code = httplib.NOT_ACCEPTABLE
    status_message = 'UNEXPECTED'
    response_code = 107000


class ValidationError(Unexpected):
    response_code = 107010
    status_message = 'VALIDATION_ERROR'
