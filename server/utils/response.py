# coding=utf-8
from __future__ import absolute_import

from flask import current_app, request, make_response, json
from functools import wraps
from pymongo.cursor import Cursor

from apiresps.errors import (APIResponse,
                             APIError,
                             ResponseInstanceTypeError)


def output_json(f):
    @wraps(f)
    def decorate(*args, **kwargs):
        result = f(*args, **kwargs)
        if isinstance(result, Cursor):
            data = list(result)
        else:
            data = result
        return make_json_response(APIResponse(data))
    return decorate


def get_output_json(result):
    if isinstance(result, Cursor):
        data = list(result)
    else:
        data = result
    try:
        return APIResponse(data)
    except Exception:
        raise ResponseInstanceTypeError


def _make_allow_headers():
    request_allows = request.headers.get('Access-Control-Request-Headers')
    if request_allows:
        return request_allows
    base_set = ['origin', 'accept', 'content-type', 'authorization']
    return ', '.join(base_set)


def make_cors_headers():
    headers = dict()
    headers['Access-Control-Allow-Headers'] = _make_allow_headers()
    headers_options = 'OPTIONS, HEAD, POST, PUT, DELETE'
    headers['Access-Control-Allow-Methods'] = headers_options

    allowed_origins = current_app.config.get('ALLOW_ORIGINS', [])
    allowed_credentials = current_app.config.get('ALLOW_CREDENTIALS')

    if '*' in allowed_origins:
        headers['Access-Control-Allow-Origin'] = '*'
    elif request.headers.get('Origin') in allowed_origins:
        headers['Access-Control-Allow-Origin'] = request.headers['Origin']

    if allowed_credentials:
        headers['Access-Control-Allow-Credentials'] = 'true'

    headers['Access-Control-Max-Age'] = 60 * 60 * 24
    return headers


def make_json_response(response_or_error, cross=True):

    if isinstance(response_or_error, APIResponse):
        output = response_or_error.data
    else:
        if not isinstance(response_or_error, APIError):
            response_or_error = ResponseInstanceTypeError()

        if request.method in ['PUT', 'POST']:
            try:
                request_body = request.json
            except Exception:
                request_body = u'Json Data Invalid'
        else:
            request_body = u''

        output = {
            'errcode': response_or_error.response_code,
            'errmsg': response_or_error.status_message,
            'hint': response_or_error.message,
            'request': {
                'api': request.path,
                'method': request.method,
                'body': request_body,
            }
        }
    headers = dict()
    headers['Content-Type'] = 'application/json'
    if cross is True:
        headers.update(make_cors_headers())
    resp = make_response(json.dumps(output),
                         response_or_error.status_code,
                         headers)
    return resp


def make_content_response(output, status_code, etag=None):
    response = make_response(output, status_code)
    response.cache_control.public = 'public'
    response.cache_control.max_age = 60 * 10
    if etag is not None:
        response.set_etag(etag)
    return response
