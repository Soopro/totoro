# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   flash,
                   url_for,
                   redirect,
                   render_template,
                   g)
import os

from utils.model import make_paginator
from utils.short_url import encode_short_url
from utils.misc import (parse_int,
                        process_slug,
                        slug_uuid_suffix,
                        parse_dateformat,
                        safe_filename,
                        uuid4_hex,
                        now)

from helpers.record import recording
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
    search_key = request.args.get('search_key', u'')
    if search_key:
        books = current_app.mongodb.Book.search(search_key.split())
    else:
        books = current_app.mongodb.Book.find_all()

    p = make_paginator(books, paged, 60)

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
    return render_template('books.html',
                           books=books,
                           p=paginator,
                           search_key=search_key)


@blueprint.route('/<book_id>')
@login_required
def detail(book_id):
    configure = g.configure

    Book = current_app.mongodb.Book
    allowed_status = [
        {'key': Book.STATUS_OFFLINE, 'text': 'Offline'},
        {'key': Book.STATUS_ONLINE, 'text': 'Online'},
    ]
    book = _find_book(book_id)
    records = current_app.mongodb.BookRecord.find_by_bookid(book['_id'])
    terms = current_app.mongodb.Term.find_all()
    vol_list = current_app.mongodb.BookVolume.find_by_bookid(book['_id'])
    volumes = []
    overtime_limit = configure['rental_time_limit']
    for vol in vol_list:
        if overtime_limit:
            vol['overtime'] = vol['rental_time'] != 0 and \
                vol['rental_time'] <= overtime_limit
        else:
            vol['overtime'] = False
        volumes.append(vol)

    return render_template('book_detail.html',
                           book=book,
                           terms=list(terms),
                           volumes=volumes,
                           records=list(records),
                           allowed_status=allowed_status)


@blueprint.route('/<book_id>', methods=['POST'])
@login_required
def update(book_id):
    slug = request.form.get('slug')
    title = request.form.get('title', u'')
    author = request.form.get('author', u'')
    publisher = request.form.get('publisher', u'')
    description = request.form.get('description', u'')
    tags = request.form.get('tags', u'')
    terms = request.form.getlist('terms') or []
    credit = request.form.get('credit', 0)
    value = request.form.get('value', 0)
    figure = request.form.get('figure', u'')
    previews = request.form.get('previews', u'')
    memo = request.form.get('memo', u'')
    status = request.form.get('status')

    book = _find_book(book_id)
    if slug:
        book['slug'] = _uniqueify_book_slug(slug, book)
    book['tags'] = [tag.strip() for tag in tags.split('|')
                    if tag.strip()]
    book['terms'] = [term.strip() for term in terms if term.strip()]
    # book['rating'] = parse_int(rating)
    book['meta'].update({
        'title': title,
        'author': author,
        'publisher': publisher,
        'description': description,
        'figure': figure,
        'previews': [preview.strip() for preview in previews.split('\n')
                     if preview.strip()],
    })
    book['credit'] = parse_int(credit)
    book['value'] = parse_int(value)
    book['status'] = parse_int(status)
    book['memo'] = memo
    book.save()

    # update all book volume to same as the book.
    current_app.mongodb.BookVolume.refresh_meta(book['_id'],
                                                book['slug'],
                                                book['meta'])
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
    title = request.form['title']
    book = current_app.mongodb.Book()
    book['slug'] = _uniqueify_book_slug(title)
    book['meta'] = {'title': title}
    book.save()
    flash('Created.')
    return_url = url_for('.detail', book_id=book['_id'])
    return redirect(return_url)


@blueprint.route('/<book_id>/volume/create', methods=['POST'])
@login_required
def create_volume(book_id):
    code = request.form.get('code')

    book = _find_book(book_id)
    volume = current_app.mongodb.BookVolume()
    volume['book_id'] = book['_id']
    volume['scope'] = book['slug']
    volume['code'] = _gen_book_code(book, code)
    volume['meta'] = book['meta']
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
    if volume and not volume['renter']:
        volume.delete()
    return_url = url_for('.detail', book_id=book['_id'])
    return redirect(return_url)


@blueprint.route('/<book_id>/attach_cover', methods=['POST'])
@login_required
def attach_cover(book_id):
    file = request.files['cover']

    book = _find_book(book_id)
    media = _upload_img(file)

    uploads_url = current_app.config.get('UPLOADS_URL')
    book['meta']['figure'] = u'{}/{}/{}'.format(uploads_url,
                                                media['scope'],
                                                media['key'])
    book.save()
    return redirect(request.referrer)


@blueprint.route('/<book_id>/attach_preview', methods=['POST'])
@login_required
def attach_preview(book_id):
    files = request.files.getlist('previews')

    book = _find_book(book_id)
    media_list = []

    for file in files[:12]:
        try:
            media_list.append(_upload_img(file))
        except Exception as e:
            flash(unicode(e), 'warning')

    uploads_url = current_app.config.get('UPLOADS_URL')
    for media in media_list:
        preview_src = u'{}/{}/{}'.format(uploads_url,
                                         media['scope'],
                                         media['key'])
        book['meta']['previews'].append(preview_src)
    book.save()

    return redirect(request.referrer)


@blueprint.route('/<book_id>/volume/<vol_id>/checkin')
@login_required
def checkin_volume(book_id, vol_id):
    book = _find_book(book_id)
    BookVolume = current_app.mongodb.BookVolume
    volume = BookVolume.find_one_by_bookid_id(book_id, vol_id)
    user = current_app.mongodb.User.find_one_by_id(volume['user_id'])
    if volume and volume['status'] == BookVolume.STATUS_LEND:
        volume['user_id'] = None
        volume['renter'] = u''
        volume['rental_time'] = 0
        volume['status'] = BookVolume.STATUS_STOCK
        volume.save()
        recording(book, volume, user, True)
    return_url = url_for('.detail', book_id=book['_id'])
    return redirect(return_url)


@blueprint.route('/<book_id>/volume/<vol_id>/checkout', methods=['POST'])
@login_required
def checkout_volume(book_id, vol_id):
    login = request.form.get('login')

    book = _find_book(book_id)

    user = current_app.mongodb.User.find_one_by_login(login)
    if not user:
        raise Exception('user not found')
    elif user['credit'] < book['credit']:
        raise Exception('Not enough credit.')

    BookVolume = current_app.mongodb.BookVolume
    volume = BookVolume.find_one_by_bookid_id(book_id, vol_id)
    if volume and volume['statis'] == BookVolume.STATUS_STOCK:
        volume['user_id'] = user['_id']
        volume['renter'] = user['login']
        volume['rental_time'] = now()
        volume['status'] = BookVolume.STATUS_LEND
        volume.save()
        user['credit'] -= book['credit']
        user.save()
        recording(book, volume, user)
    return_url = url_for('.detail', book_id=book['_id'])
    return redirect(return_url)


@blueprint.route('/category')
@login_required
def category():
    terms = current_app.mongodb.Term.find_all()
    return render_template('category.html', terms=list(terms))


@blueprint.route('/category/create', methods=['POST'])
@login_required
def create_term():
    name = request.form['name']
    term = current_app.mongodb.Term()
    term['key'] = _uniqueify_term_key(name)
    term['meta'] = {'name': name}
    term.save()
    flash('Created.')
    return redirect(request.referrer)


@blueprint.route('/category/<term_id>')
@login_required
def term_detail(term_id):
    term = _find_term(term_id)
    return render_template('term.html', term=term)


@blueprint.route('/category/<term_id>/update', methods=['POST'])
@login_required
def update_term(term_id):
    key = request.form.get('key')
    name = request.form.get('name', u'')
    figure = request.form.get('figure', u'')

    term = _find_term(term_id)
    if key:
        term['key'] = _uniqueify_term_key(key, term)
    term['meta'].update({
        'name': name,
        'figure': figure
    })
    term.save()
    return_url = url_for('.category')
    return redirect(return_url)


@blueprint.route('/category/<term_id>/update')
@login_required
def remove_term(term_id):
    term = _find_term(term_id)
    term.delete()
    return_url = url_for('.category')
    return redirect(return_url)


@blueprint.route('/print')
@login_required
def print_volumes():
    paged = parse_int(request.args.get('paged'), 1, True)

    volumes = current_app.mongodb.BookVolume.find_all()
    p = make_paginator(volumes, paged, 20)
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

    return render_template('print_volumes.html',
                           volumes=list(volumes),
                           p=paginator)


# helpers
def _find_book(book_id):
    book = current_app.mongodb.Book.find_one_by_id(book_id)
    if not book:
        raise Exception('Book not found ...')
    return book


def _find_term(term_id):
    term = current_app.mongodb.Term.find_one_by_id(term_id)
    if not term:
        raise Exception('Term not found ...')
    return term


def _uniqueify_book_slug(slug, book=None):
    slug = process_slug(slug)
    if book and slug == book['slug']:
        # don't process if it self.
        return slug

    _book = current_app.mongodb.Book.find_one_by_slug(slug)
    if _book is not None:
        slug = slug_uuid_suffix(slug)
        slug = _uniqueify_book_slug(slug, book)

    return slug


def _uniqueify_term_key(key, term=None):
    key = process_slug(key)
    if term and key == term['key']:
        # don't process if it self.
        return key

    _term = current_app.mongodb.Term.find_one_by_key(key)
    if _term is not None:
        key = slug_uuid_suffix(key)
        key = _uniqueify_term_key(key, term)

    return key


def _gen_book_code(book, code=None):
    if not code:
        code = unicode(encode_short_url())
    _book = current_app.mongodb.\
        BookVolume.find_one_by_bookid_code(book['_id'], code)
    if _book is not None:
        code = _gen_book_code(book, unicode(encode_short_url(12)))
    return code


def _allowed_book_file(filename):
    file_ext = ''
    allowed_exts = current_app.config.get('ALLOWED_MEDIA_EXTS')
    if '.' in filename:
        file_ext = filename.rsplit('.', 1)[1]
    return file_ext.lower() in allowed_exts


def _upload_img(file):
    if not file or not _allowed_book_file(file.filename):
        raise Exception('{} file not allowed.'.format(file.filename))

    scope = parse_dateformat(now(), '%Y-%m')
    key = filename = safe_filename(file.filename)
    media = current_app.mongodb.Media.find_one_by_scope_key(scope, key)

    if media:  # rename file if exists.
        fname, ext = os.path.splitext(filename)
        key = filename = u'{}-{}{}'.format(fname, uuid4_hex(), ext)

    media = current_app.mongodb.Media()
    media['scope'] = scope
    media['filename'] = filename
    media['key'] = key
    media['mimetype'] = unicode(file.mimetype)
    media['size'] = parse_int(file.content_length)
    media.save()

    uplaods_dir = current_app.config.get('UPLOADS_FOLDER')
    uploads_folder = os.path.join(uplaods_dir, scope)
    if not os.path.isdir(uploads_folder):
        try:
            os.makedirs(uploads_folder)
        except Exception:
            pass
    file.save(os.path.join(uploads_folder, key))

    return media
