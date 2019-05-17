# coding=utf-8
from __future__ import absolute_import

from flask import g, current_app, abort, request
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


def verify_remote():
    ref_url = current_app.mongodb.Configuration.MINI_REFERRER_URL
    if current_app.debug:
        print 'referrer_url:', ref_url
        print 'request.referrer:', request.referrer
        print '---------------------------'
    if request.referrer and request.referrer.startswith(ref_url):
        ref_path = request.referrer.replace(ref_url, '').strip('/')
        mina_app_id = ref_path.split('/')[0]
        if mina_app_id != g.configure['mina_app_id']:
            abort(403)
    else:
        abort(403)
        return
