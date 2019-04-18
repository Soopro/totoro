# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   flash,
                   url_for,
                   redirect,
                   render_template)

from utils.model import make_paginator
from utils.misc import parse_int

from admin.decorators import login_required


blueprint = Blueprint('user', __name__, template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    paged = parse_int(request.args.get('paged'), 1, True)
    deleted = parse_int(request.args.get('deleted'), 0)

    User = current_app.mongodb.User
    if deleted:
        users = User.find_dead()
    else:
        users = User.find_alive()

    p = make_paginator(users, paged, 12)

    prev_url = url_for(request.endpoint,
                       paged=p.previous_page,
                       deleted=deleted)
    next_url = url_for(request.endpoint,
                       paged=p.next_page,
                       deleted=deleted)

    paginator = {
        'next': next_url if p.has_next else None,
        'prev': prev_url if p.has_previous and p.previous_page else None,
        'paged': p.current_page,
        'start': p.start_index,
        'end': p.end_index,
    }
    return render_template('users.html', users=users, p=paginator)


@blueprint.route('/<user_id>')
@login_required
def detail(user_id=None):
    User = current_app.mongodb.User

    user = _find_user(user_id)
    allowed_status = [
        {'key': User.STATUS_DEACTIVATED, 'text': 'Deactivated'},
        {'key': User.STATUS_ACTIVATED, 'text': 'Activated'},
        {'key': User.STATUS_BANNED, 'text': 'Banned'}
    ]
    return render_template('user_detail.html',
                           user=user,
                           allowed_status=allowed_status)


@blueprint.route('/<user_id>', methods=['POST'])
@login_required
def update(user_id):
    status = request.form.get('status')

    user = _find_user(user_id)
    user['status'] = parse_int(status)
    user.save()
    flash('Saved.')
    return_url = url_for('.detail', user_id=user['_id'])
    return redirect(return_url)


@blueprint.route('/<user_id>/remove')
@login_required
def remove(user_id):
    user = _find_user(user_id)
    user.remove()
    return_url = url_for('.index')
    return redirect(return_url)


# helpers
def _find_user(user_id):
    user = current_app.mongodb.User.find_one_by_id(user_id)
    if not user:
        raise Exception('User not found...')
    return user
