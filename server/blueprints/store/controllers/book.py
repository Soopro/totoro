# coding=utf-8
from __future__ import absolute_import

from flask import current_app

from utils.response import output_json
from utils.request import get_args, get_param
from utils.misc import parse_int
from utils.model import make_offset_paginator, attach_extend

from apiresps.validations import Struct

from ..errors import BookNotFound


@output_json
def list_books():
    offset = parse_int(get_args('offset'), 0, 0)
    limit = parse_int(get_args('limit'), 24, 1)
    term = get_args('term')

    books = current_app.mongodb.Book.find_activated(term)
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
    return output_book(book)


@output_json
def search():
    offset = get_param('offset', Struct.Int, 0)
    limit = get_param('limit', Struct.Int, 24)
    search_keys = get_param('search_keys', Struct.List)

    search_keys = [k for k in search_keys if isinstance(k, unicode) and k]
    if not search_keys:
        return []

    books = current_app.mongodb.Book.search(search_keys)
    p = make_offset_paginator(books, offset, limit)
    return attach_extend(
        [output_book(book) for book in books],
        {'_more': p.has_more, '_count': p.count}
    )


# outputs
def output_book(book):
    return {
        'id': book['_id'],
        'slug': book['slug'],
        'terms': book['terms'],
        'tags': book['tags'],
        'meta': book['meta'],
        'status': book['status'],
        'creation': book['creation'],
        'updated': book['updated'],
    }
