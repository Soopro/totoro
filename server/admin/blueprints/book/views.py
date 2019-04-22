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
from utils.short_url import encode_short_url
from utils.misc import parse_int, process_slug, slug_uuid_suffix

from admin.decorators import login_required


blueprint = Blueprint('book',
                      __name__,
                      static_folder='static',
                      static_url_path='/static',
                      template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    paged = parse_int(request.args.get('paged'), 1, True)

    books = current_app.mongodb.Book.find_all()

    p = make_paginator(books, paged, 12)

    prev_url = url_for(request.endpoint,
                       paged=p.previous_page)
    next_url = url_for(request.endpoint,
                       paged=p.next_page)

    paginator = {
        'next': next_url if p.has_next else None,
        'prev': prev_url if p.has_previous and p.previous_page else None,
        'paged': p.current_page,
        'start': p.start_index,
        'end': p.end_index,
    }
    return render_template('books.html', books=books, p=paginator)


@blueprint.route('/<book_id>')
@login_required
def detail(book_id):
    Book = current_app.mongodb.Book
    allowed_status = [
        {'key': Book.STATUS_OFFLINE, 'text': 'Offline'},
        {'key': Book.STATUS_ONLINE, 'text': 'Online'},
    ]
    book = _find_book(book_id)
    volumes = current_app.mongodb.BookVolume.find_by_bookid(book['_id'])
    records = current_app.mongodb.BookRecord.find_by_bookid(book['_id'])
    return render_template('book_detail.html',
                           book=book,
                           volumes=list(volumes),
                           records=list(records),
                           allowed_status=allowed_status)


@blueprint.route('/<book_id>', methods=['POST'])
@login_required
def update(book_id):
    slug = request.form.get('slug')
    title = request.form.get('title')
    description = request.form.get('description')
    tags = request.form.get('tags')
    category = request.form.get('category')
    # rating = request.form.get('rating')
    cover_src = request.form.get('cover_src')
    previews = request.form.get('previews')

    status = request.form.get('status')

    book = _find_book(book_id)
    if slug:
        book['slug'] = _uniqueify_book_slug(slug, book)
    book['tags'] = [tag.strip() for tag in tags.split('|')]
    book['category'] = [cat.strip() for cat in category.split('\n')]
    # book['rating'] = parse_int(rating)
    book['meta'].update({
        'title': title,
        'description': description,
        'cover_src': cover_src,
        'previews': [preview.strip() for preview in previews.split('\n')],
    })
    book['status'] = parse_int(status)
    book.save()
    flash('Saved.')
    return_url = url_for('.detail', book_id=book['_id'])
    return redirect(return_url)


@blueprint.route('/<book_id>/remove')
@login_required
def remove(book_id):
    book = _find_book(book_id)
    count_volumes = current_app.mongodb.BookVolume.count_used(book_id)
    if count_volumes <= 0:
        book.delete()
        flash('Removed.')
        return_url = url_for('.index')
    else:
        flash('Remove all volumes before delete.', 'danger')
        return_url = url_for('.detail', book_id=book['_id'])
    return redirect(return_url)


@blueprint.route('/create', methods=['POST'])
@login_required
def create():
    slug = request.form['slug']
    book = current_app.mongodb.Book()
    book['slug'] = _uniqueify_book_slug(slug)

    book.save()
    flash('Created.')
    return_url = url_for('.detail', book_id=book['_id'])
    return redirect(return_url)


@blueprint.route('/<book_id>/volume/create', methods=['POST'])
@login_required
def create_volume(book_id):
    serial_number = request.form['serial_number']
    code = request.form.get('code')

    book = _find_book(book_id)
    volume = current_app.mongodb.BookVolume()
    volume['book_id'] = book['_id']
    volume['serial_number'] = serial_number
    volume['code'] = _gen_book_code(book, code)
    volume.save()
    flash('Volume created.')
    return_url = url_for('.detail', book_id=book['_id'])
    return redirect(return_url)


@blueprint.route('/<book_id>/volume/<vol_id>/remove')
@login_required
def remove_volume(book_id, vol_id):
    book = _find_book(book_id)
    volume = current_app.mongodb.\
        BookVolume.find_one_by_bookid_id(book_id, vol_id)
    if volume:
        volume.delete()
    return_url = url_for('.detail', book_id=book['_id'])
    return redirect(return_url)


# helpers
def _find_book(book_id):
    book = current_app.mongodb.Book.find_one_by_id(book_id)
    if not book:
        raise Exception('Book not found ...')
    return book


def _uniqueify_book_slug(slug, book=None):
    slug = process_slug(slug)
    if book and slug == book['slug']:
        # don't process if the content_file it self.
        return slug

    _book = current_app.mongodb.Book.find_one_by_slug(slug)
    if _book is not None:
        slug = slug_uuid_suffix(slug)
        slug = _uniqueify_book_slug(slug, book)

    return slug


def _gen_book_code(book, code=None):
    if not code:
        code = unicode(encode_short_url(12))
    _book = current_app.mongodb.\
        BookVolume.find_one_by_bookid_code(book['_id'], code)
    if _book is not None:
        code = _gen_book_code(book, unicode(encode_short_url(12)))
    return code
