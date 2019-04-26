# coding=utf-8
from __future__ import absolute_import

from flask import current_app
from bson import ObjectId

from utils.auth import load_token, load_payload

from apiresps.errors import (Unauthorized,
                             PermissionDenied)


def get_current_user():
    User = current_app.mongodb.User

    payload = load_payload(load_token())
    try:
        uid = ObjectId(payload['user_id'])  # to make sure it is ObjectId
    except Exception:
        raise Unauthorized('invalid token')

    user = User.find_one_by_id(uid)

    if not user:
        raise Unauthorized('not found')
    elif user['status'] == User.STATUS_BANNED:
        raise PermissionDenied('banned')

    return user


def get_current_configure():
    configure = current_app.mongodb.Configuration.get_conf() or {}
    if not configure:
        raise PermissionDenied('configure')
    return configure
