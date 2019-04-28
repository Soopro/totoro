# coding=utf-8
from __future__ import absolute_import

from flask import Blueprint, request

from utils.misc import route_inject

from .routes import urlpatterns


bp_name = 'configure'

blueprint = Blueprint(bp_name, __name__)

route_inject(blueprint, urlpatterns)

# endpoint types
open_api_endpoints = [
    '{}.get_configure'.format(bp_name),
]


@blueprint.before_request
def before():
    if request.endpoint in open_api_endpoints:
        pass
