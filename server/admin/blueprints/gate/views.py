# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   session,
                   request,
                   redirect,
                   url_for,
                   flash,
                   render_template)

from utils.auth import check_hashed_password, generate_hashed_password
from utils.request import get_remote_addr
from utils.misc import hmac_sha

from admin.decorators import login_required


blueprint = Blueprint('gate', __name__, template_folder='pages')


@blueprint.route('/login')
def login():
    configure = current_app.mongodb.Configuration.get_conf()
    if not configure:
        return redirect(url_for('.initialize'))
    elif session.get('admin'):
        return redirect('/')
    return render_template('login.html')


@blueprint.route('/login', methods=['POST'])
def exec_login():
    configure = current_app.mongodb.Configuration.get_conf()
    passcode = request.form['passcode']
    if not configure:
        return redirect(url_for('.initialize'))
    elif check_hashed_password(configure['passcode_hash'], passcode):
        hmac_key = u'{}{}'.format(current_app.secret_key, get_remote_addr())
        session['admin'] = hmac_sha(hmac_key, configure['passcode_hash'])
        return redirect('/')
    else:
        flash('Wrong passcode!')
        return redirect(url_for('.login'))


@blueprint.route('/initialize')
def initialize():
    configure = current_app.mongodb.Configuration.get_conf()
    if configure:
        return redirect(url_for('.login'))
    return render_template('initialize.html')


@blueprint.route('/initialize', methods=['POST'])
def exec_initialize():
    passcode = request.form['passcode']
    passcode2 = request.form['passcode2']
    mina_app_id = request.form.get('mina_app_id', u'')
    mina_app_secret = request.form.get('mina_app_secret', u'')

    if passcode != passcode2:
        raise Exception('Passcode not match ...')

    configure = current_app.mongodb.Configuration.get_conf()
    configure['passcode_hash'] = generate_hashed_password(passcode)
    configure['mina_app_id'] = mina_app_id
    configure['mina_app_secret'] = mina_app_secret
    if not configure:
        return redirect('/initialize')
    elif session.get('admin'):
        return redirect('/')
    return render_template('login.html')


@blueprint.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('.login'))