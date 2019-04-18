# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   session,
                   request,
                   flash,
                   url_for,
                   redirect,
                   render_template)

from utils.auth import generate_hashed_password
from utils.request import get_remote_addr
from utils.misc import hmac_sha

from admin.decorators import login_required


blueprint = Blueprint('configuration', __name__, template_folder='pages')


@blueprint.route('/')
@login_required
def configuration():
    configure = _get_configuration()
    return render_template('configuration.html', configure=configure)


@blueprint.route('/', methods=['POST'])
@login_required
def update_configuration():
    mina_app_id = request.form.get('mina_app_id')
    mina_app_secret = request.form.get('mina_app_secret')
    passcode = request.form.get('passcode')
    passcode2 = request.form.get('passcode2')

    configure = _get_configuration()
    configure['mina_app_id'] = mina_app_id
    configure.encrypt('mina_app_secret', mina_app_secret)
    if passcode and passcode == passcode2:
        configure['passcode_hash'] = generate_hashed_password(passcode)
        hmac_key = u'{}{}'.format(current_app.secret_key, get_remote_addr())
        session['admin'] = hmac_sha(hmac_key, configure['passcode_hash'])
    configure.save()
    flash('Saved.')
    return_url = url_for('.configuration')
    return redirect(return_url)


# helpers
def _get_configuration():
    configuration = current_app.mongodb.Configuration.get_conf()
    if not configuration:
        raise Exception('Configuration not found...')
    return configuration
