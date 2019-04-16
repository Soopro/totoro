# coding=utf-8
from __future__ import absolute_import

from flask import current_app, request
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import timedelta

from itsdangerous import (TimedJSONWebSignatureSerializer,
                          JSONWebSignatureSerializer,
                          SignatureExpired,
                          BadSignature)

from apiresps.errors import Unauthorized, PermissionExpired


def get_timed_serializer(expires_in=None, salt=None):
    if not isinstance(salt, basestring):
        salt = current_app.config.get('JWT_SALT')

    if expires_in is None:
        expires_in = current_app.config.get('JWT_EXPIRATION_DELTA', 0)
    if isinstance(expires_in, timedelta):
        expires_in = int(expires_in.total_seconds())

    expires_in = expires_in + current_app.config.get('JWT_LEEWAY', 0)
    secret_key = current_app.config.get('JWT_SECRET_KEY')
    algorithm_name = current_app.config.get('JWT_ALGORITHM', 'HS256')
    return TimedJSONWebSignatureSerializer(secret_key=secret_key,
                                           expires_in=expires_in,
                                           salt=salt,
                                           algorithm_name=algorithm_name)


def get_serializer(salt=None):
    if not isinstance(salt, basestring):
        salt = current_app.config.get('JWT_SALT')
    secret_key = current_app.config.get('JWT_SECRET_KEY')
    algorithm_name = current_app.config.get('JWT_ALGORITHM', 'HS256')
    return JSONWebSignatureSerializer(secret_key=secret_key,
                                      salt=salt,
                                      algorithm_name=algorithm_name)


def load_token(prefix=None):
    key = current_app.config['JWT_AUTH_HEADER_KEY']
    token_prefix = prefix or current_app.config['JWT_AUTH_HEADER_PREFIX']
    auth = request.headers.get(key, None)

    if auth is None:
        raise Unauthorized('Authorization Required')

    parts = auth.split()

    if parts[0].lower() != token_prefix.lower():
        raise Unauthorized('Invalid JWT header: unsupported')
    elif len(parts) == 1:
        raise Unauthorized('Invalid JWT header: missing')
    elif len(parts) > 2:
        raise Unauthorized('Invalid JWT header: contains spaces')
    return parts[1]


def load_payload(payload, timed=True, salt=None):
    try:
        if timed:
            return get_timed_serializer(salt=salt).loads(payload)
        else:
            return get_serializer(salt=salt).loads(payload)
    except SignatureExpired:
        raise PermissionExpired('Signature expired')
    except BadSignature:
        raise Unauthorized('Signature undecipherable')


def generate_token(payload, expires_in=None, salt=None):
    payload = _safe_payload(payload)
    ts = get_timed_serializer(expires_in=expires_in, salt=salt)
    return ts.dumps(payload).decode('utf-8')


def generate_hashed_password(password):
    return unicode(generate_password_hash(unicode(password)))


def check_hashed_password(hashed, password):
    return check_password_hash(str(hashed), password)


# helpers
def _safe_payload(payload):
    if isinstance(payload, dict):
        new_payload = {}
        for k, v in payload.iteritems():
            new_payload[k] = _safe_payload(v)
    elif isinstance(payload, list):
        new_payload = []
        for item in payload:
            new_payload.append(_safe_payload(item))
    elif not isinstance(payload, (int, float, bool)):
        new_payload = unicode(payload)
    else:
        new_payload = payload
    return new_payload
