# coding=utf-8
from __future__ import absolute_import

from flask import current_app, g

from utils.auth import generate_token

from utils.response import output_json
from utils.request import get_param

from services.wechat import WeChatMinaAPI

from apiresps.validations import Struct

from ..errors import UserMinaSessionError


@output_json
def login():
    code = get_param('code', Struct.Code, True)

    configure = g.configure
    mina = WeChatMinaAPI(app_id=configure['mina_app_id'],
                         app_secret=configure.decrypt('mina_app_secret'),
                         redis_read=current_app.redis)
    try:
        mina_session = mina.get_session(code)
    except Exception as e:
        raise UserMinaSessionError(e)

    User = current_app.mongodb.User
    user = User.find_one_by_openid(mina_session['openid'])
    if not user:
        user = User()
        user['openid'] = unicode(mina_session['openid'])
        user.save()

    token = generate_token({
        'openid': user['openid'],
        'session_key': mina_session['session_key'],
    })

    expires_in = current_app.config.get('JWT_EXPIRATION_DELTA')

    return {
        'token': token,
        'expires_in': expires_in,
        'is_activated': user['status'] == User.STATUS_ACTIVATED
    }


@output_json
def join_member():
    encrypted_data = get_param('encrypted_data', Struct.Code, True)
    iv = get_param('iv', Struct.Code, True)

    user = g.curr_user
    configure = g.configure
    wx_mini = WeChatMinaAPI(app_id=configure['mina_app_id'],
                            app_secret=configure.decrypt('mina_app_secret'),
                            redis_read=current_app.redis)
    try:
        phone = wx_mini.get_bound_phone(user['session_key'],
                                        encrypted_data,
                                        iv)
        login = phone['phonenum']
    except Exception as e:
        raise UserMinaSessionError(e)

    # attach user login
    current_app.mongodb.User.displace_login(login, user['openid'])
    # use to displace other user might have share same login.
    user['login'] = login
    user['status'] = current_app.mongodb.User.STATUS_ACTIVATED
    user.save()

    return output_profile(user)


@output_json
def get_profile():
    user = g.curr_user
    return output_profile(user)


@output_json
def update_profile():
    meta = get_param('meta', Struct.Dict, default={})

    user = g.curr_user
    user['meta'] = meta
    user.save()
    return output_profile(user)


# outputs
def output_profile(user):
    return {
        'id': user['_id'],
        'login': user['login'],
        'meta': user['meta'],
        'status': user['status'],
        'creation': user['creation'],
        'updated': user['updated'],
    }
