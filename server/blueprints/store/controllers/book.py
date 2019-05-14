# coding=utf-8
from __future__ import absolute_import

from flask import current_app, g

from utils.response import output_json
from utils.request import get_args, get_param
from utils.misc import parse_int, now
from utils.model import make_offset_paginator, attach_extend

from apiresps.validations import Struct

from ..errors import (BookNotFound,
                      BookNotEnoughVolume,
                      BookNotEnoughCredit,
                      BookReachBorrowLimit)


@output_json
def list_books():
    offset = parse_int(get_args('offset'), 0, 0)
    limit = parse_int(get_args('limit'), 24, 1)
    term = get_args('term')
    timestamp = get_args('t', Struct.Int)

    books = current_app.mongodb.Book.find_activated(term, timestamp)
    p = make_offset_paginator(books, offset, limit)
    return attach_extend(
        [output_book(book) for book in books],
        {'_more': p.has_more, '_count': p.count}
    )


@output_json
def get_book(book_slug):
    book = current_app.mongodb.Book.find_one_by_slug(book_slug)
    if not book:
        raise BookNotFound
    return output_book(book, True)


@output_json
def checkin_book():
    slug = get_param('slug', Struct.Attr, True)

    user = g.curr_user

    BookVolume = current_app.mongodb.BookVolume
    book = current_app.mongodb.Book.find_one_by_slug(slug)
    if not book:
        raise BookNotFound
    elif user['credit'] < book['credit']:
        raise BookNotEnoughCredit
    elif BookVolume.count_lend(user['_id']) > BookVolume.MAX_LEND:
        raise BookReachBorrowLimit

    volume = BookVolume.find_one_stocked_by_bookid(book['_id'])
    if volume:
        volume['user_id'] = user['_id']
        volume['borrower'] = user['login']
        volume['borrowing_time'] = now()
        volume['status'] = BookVolume.STATUS_PENDING
        volume.save()

        user['credit'] -= book['credit']
        user.save()

        BookRecord = current_app.mongodb.BookRecord
        record = BookRecord()
        record['user_id'] = user['_id']
        record['book_id'] = book['_id']
        record['borrower'] = user['login']
        record['volume'] = volume['code']
        record['meta'] = {
            'title': book['meta'].get('title', '-')
        }
        record['status'] = BookRecord.STATUS_CHECKOUT
        record.save()
    else:
        raise BookNotEnoughVolume

    return output_book(book)


@output_json
def search_books():
    search_keys = get_param('search_keys', Struct.List)

    search_keys = [k for k in search_keys if isinstance(k, unicode) and k]
    if not search_keys:
        return []

    books = current_app.mongodb.Book.search(search_keys)
    return [output_book(book) for book in books]


# outputs
def output_book(book, has_count=False):
    if has_count:
        vol_count = current_app.mongodb.\
            BookVolume.count_stocked(book['_id'])
    else:
        vol_count = None
    return {
        'id': book['_id'],
        'slug': book['slug'],
        'terms': book['terms'],
        'tags': book['tags'],
        'meta': book['meta'],
        'credit': book['credit'],
        'value': book['value'],
        'vol_count': vol_count,
        'status': book['status'],
        'creation': book['creation'],
        'updated': book['updated'],
    }
