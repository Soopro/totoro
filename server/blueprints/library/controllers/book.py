# coding=utf-8
from __future__ import absolute_import

from flask import current_app

from utils.response import output_json
from utils.request import get_args
from utils.misc import parse_int
from utils.model import make_offset_paginator, attach_extend

from ..errors import BookNotFound


@output_json
def list_books():
    offset = parse_int(get_args('offset'), 0, 0)
    limit = parse_int(get_args('limit'), 60, 1)
    term = get_args('term')

    books = current_app.mongodb.Book.find_activated(term)
    p = make_offset_paginator(books, offset, limit)
    return attach_extend(
        [output_book(book) for book in books],
        {'_more': p.has_more, '_count': p.count}
    )


@output_json
def get_book(book_id):
    book = current_app.mongodb.Book.find_one_by_id(book_id)
    if not book:
        raise BookNotFound
    return output_book(book)


# outputs
def output_book(book):
    return {
        'id': book['_id'],
        'terms': book['terms'],
        'tags': book['tags'],
        'meta': book['meta'],
        'status': book['status'],
        'creation': book['creation'],
        'updated': book['updated'],
    }
