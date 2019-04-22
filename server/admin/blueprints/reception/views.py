# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   session,
                   request,
                   flash,
                   url_for,
                   redirect,
                   render_template,
                   g)

from utils.auth import generate_hashed_password, check_hashed_password
from utils.request import get_remote_addr
from utils.misc import hmac_sha

from admin.decorators import login_required


blueprint = Blueprint('reception', __name__, template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    return render_template('reception.html', configure=configure)


@blueprint.route('/checkout', methods=['POST'])
@login_required
def checkout():
    slug = request.form.get('slug')
    volume = request.form.get('volume')


    flash('Checkout.')
    return_url = url_for('.index')
    return redirect(return_url)


@blueprint.route('/checkin', methods=['POST'])
@login_required
def checkin():
    slug = request.form.get('slug')
    volume = request.form.get('volume')

    book = _find_book_volume(slug, volume)
    if book:
        record = _find_book_record(book)

        flash('Checkin.')
    else:
        flash('No book or volume.', 'danger')
    return_url = url_for('.index')
    return redirect(return_url)


# helpers
def _find_book_volume(slug, volume):
    if not slug or not volume:
        return None

    book = current_app.mongodb.Book.find_one_by_slug(slug)
    if not book or volume not in book['volumes']:
        return None
    return book


def _find_book_record(book):
    record = current_app.mongodb.BookRecord.find_one_by_bookid(book['_id'])
    if not record:
        return None
    return book
