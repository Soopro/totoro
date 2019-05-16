# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   flash,
                   url_for,
                   redirect,
                   render_template)

from admin.decorators import login_required
from utils.misc import now

from helpers.record import recording


blueprint = Blueprint('reception', __name__, template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    return render_template('reception.html')


@blueprint.route('/checkout', methods=['POST'])
@login_required
def checkout():
    user_login = request.form['user_login']
    book_slug = request.form['book_slug']
    volume_code = request.form['volume_code']

    user = current_app.mongodb.User.find_one_by_login(user_login)
    if not user:
        flash('User not found.')

    book, volume = _find_book_volume(book_slug, volume_code)
    BookVolume = current_app.mongodb.BookVolume

    if book and volume:
        if user['credit'] < book['credit']:
            flash('Not enough credit.', 'warning')
        elif user['status'] != current_app.mongodb.User.STATUS_ACTIVATED:
            flash('user not activated', 'warning')
        elif volume['status'] == BookVolume.STATUS_STOCK:
            volume['user_id'] = user['_id']
            volume['renter'] = user['login']
            volume['rental_time'] = now()
            volume['status'] = BookVolume.STATUS_LEND
            volume.save()
            user['credit'] -= book['credit']
            user.save()
            recording(book, volume, user)
            flash('Checkout.')
        else:
            flash('Book volume already lend by {}'.format(user['login']),
                  'warning')
    else:
        flash('No book or volume.', 'danger')
    return_url = url_for('.index')
    return redirect(return_url)


@blueprint.route('/checkin', methods=['POST'])
@login_required
def checkin():
    user_login = request.form['user_login']
    book_slug = request.form['book_slug']
    volume_code = request.form['volume_code']

    user = current_app.mongodb.User.find_one_by_login(user_login)
    if not user:
        flash('User not found.')

    book, volume = _find_book_volume(book_slug, volume_code)
    BookVolume = current_app.mongodb.BookVolume
    if volume:
        if volume['status'] == BookVolume.STATUS_LEND:
            volume['user_id'] = None
            volume['renter'] = u''
            volume['rental_time'] = 0
            volume['status'] = BookVolume.STATUS_STOCK
            volume.save()
            recording(book, volume, user, True)
            flash('Checkin.')
        else:
            flash('Book volume is in stock', 'warning')
    else:
        flash('No book or volume.', 'danger')
    return_url = url_for('.index')
    return redirect(return_url)


# helpers
def _find_book_volume(book_slug, volume_code):
    if not book_slug or not volume_code:
        return None

    book = current_app.mongodb.Book.find_one_by_slug(book_slug)
    if not book:
        return None
    volume = current_app.mongodb.\
        BookVolume.find_one_by_bookid_code(book['_id'], volume_code)
    return book, volume
