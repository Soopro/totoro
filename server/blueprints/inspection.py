# coding=utf-8
from __future__ import absolute_import

from flask import g, current_app
from bson import ObjectId
from utils.auth import load_token, load_payload

from apiresps.errors import (Unauthorized,
                             PermissionDenied)


def verify_jwt():
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
    g.curr_session_key = payload['session_key']
    g.curr_user = user

    return
