# coding=utf-8
from __future__ import absolute_import

from functools import wraps
from flask import current_app, session, redirect, url_for
from utils.request import get_remote_addr
from utils.misc import hmac_sha


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('user') or \
           session['user'] != hmac_sha(current_app.secret_key,
                                       get_remote_addr()):
            session.clear()
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper
