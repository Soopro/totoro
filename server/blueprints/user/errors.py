# coding=utf-8
from __future__ import absolute_import

from apiresps.errors import Unauthorized


class UserMinaSessionError(Unauthorized):
    response_code = 400001
    status_message = 'USER_MINA_SESSION_ERROR'
