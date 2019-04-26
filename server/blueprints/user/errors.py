# coding=utf-8
from __future__ import absolute_import

from apiresps.errors import (InternalServerError,
                             BadRequest)


class UserMinaSessionError(BadRequest):
    response_code = 903003
    status_message = 'USER_MINA_SESSION_ERROR'


class UserNotActivated(InternalServerError):
    response_code = 700004
    status_message = 'USER_NOT_ACTIVATED'


class UserBlocked(InternalServerError):
    response_code = 700005
    status_message = 'USER_BLOCKED'
