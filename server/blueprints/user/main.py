# coding=utf-8
from __future__ import absolute_import

from flask import Blueprint, request

from utils.misc import route_inject

from ..inspection import verify_jwt

from .routes import urlpatterns


bp_name = 'user'

blueprint = Blueprint(bp_name, __name__)

route_inject(blueprint, urlpatterns)

# endpoint types
open_api_endpoints = [
    '{}.login'.format(bp_name),
]


@blueprint.before_request
def before():
    if request.endpoint in open_api_endpoints:
        pass
    else:
        verify_jwt()
