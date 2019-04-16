# coding=utf-8
from __future__ import absolute_import

from flask import request

from apiresps.errors import (InvalidRequest,
                             ParameterRequired,
                             RequestSourceNotExists)


def _check_request_source(req_type):
    try:
        source = getattr(request, req_type)
    except Exception:
        raise InvalidRequest
    if source is None:
        raise RequestSourceNotExists
    if not isinstance(source, dict):
        raise InvalidRequest
    return source


def _empty_value(value):
    return value is not False and value != 0 and not bool(value)


def get_param(key, validator=None, required=False, default=None):
    source = _check_request_source('json')
    value = source.get(key)

    if _empty_value(value):
        if default is not None:
            value = default
        elif required:
            raise ParameterRequired(key)

    if validator:
        validators = validator if isinstance(validator, list) else [validator]
        for vld in validators:
            vld(value, name=key, non_empty=required)

    return value


def get_field(key, validator=None, required=False, default=None):
    source = _check_request_source('form')
    value = source.get(key)

    if _empty_value(value):
        if default is not None:
            value = default
        elif required:
            raise ParameterRequired(key)

    if validator:
        validators = validator if isinstance(validator, list) else [validator]
        for vld in validators:
            vld(value, name=key, non_empty=required)

    return value


def get_args(key, required=False, default=None, multiple=False):
    source = _check_request_source('args')
    if multiple:
        value = source.getlist(key)
    else:
        value = source.get(key)

    if _empty_value(value):
        if default is not None:
            value = default
        elif required:
            raise ParameterRequired(key)

    return value


def parse_args():
    new = dict()
    args = request.args
    for arg in args:
        if arg in new:
            if not isinstance(new[arg], list):
                new[arg] = [new[arg]]
            new[arg].append(args.get(arg))
        else:
            new[arg] = args.get(arg)
    return new


def get_remote_addr():
    ip = request.headers.get('X-Forwarded-For')
    if ip:
        ip = ip.split(',', 1)[0]
    else:
        ip = request.headers.get('X-Real-IP')
    return ip or request.remote_addr


def get_request_url(base_url, path):
    if '?' in request.url:
        args = request.url.split('?', 1)[1]
        return '{}{}?{}'.format(base_url, path, args)
    else:
        return '{}{}'.format(base_url, path)


def get_request_headers():
    try:
        return dict(request.headers)
    except Exception:
        return {}
