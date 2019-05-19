# coding=utf-8
from __future__ import absolute_import

from flask import current_app, g

from utils.response import output_json
from utils.request import get_args, get_param
from utils.misc import parse_int, now
from utils.model import make_offset_paginator, attach_extend

from helpers.record import recording
from apiresps.validations import Struct

from ..errors import (BookNotFound,
                      BookNotEnoughVolume,
                      BookNotEnoughCredit,
                      BookReachRentLimit)


@output_json
def list_books():
    offset = parse_int(get_args('offset'), 0, 0)
    limit = parse_int(get_args('limit'), 12, 1)
    term = get_args('term')
    timestamp = get_args('t', Struct.Int)
    print 'offset', offset
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
    return output_single_book(book)


@output_json
def checkout_book(book_slug):
    recipient = get_param('recipient', Struct.Desc, True)

    user = g.curr_user

    BookVolume = current_app.mongodb.BookVolume
    book = current_app.mongodb.Book.find_one_by_slug(book_slug)
    if not book:
        raise BookNotFound
    elif user['credit'] < book['credit']:
        raise BookNotEnoughCredit
    elif BookVolume.count_lend(user['_id']) > BookVolume.MAX_LEND:
        raise BookReachRentLimit

    volume = BookVolume.find_one_stocked_by_bookid(book['_id'])
    if volume:
        volume['user_id'] = user['_id']
        volume['renter'] = recipient or user['login']
        volume['rental_time'] = now()
        volume['status'] = BookVolume.STATUS_PENDING
        volume.save()
        user['credit'] -= book['credit']
        user.save()
        recording(book, volume, user)
    else:
        raise BookNotEnoughVolume

    return output_single_book(book)


@output_json
def search_books():
    search_keys = get_param('search_keys', Struct.List)

    search_keys = [k for k in search_keys if isinstance(k, unicode) and k]
    if not search_keys:
        return []

    books = current_app.mongodb.Book.search(search_keys)
    return [output_book(book) for book in books]


# outputs
def output_book(book):
    return {
        'id': book['_id'],
        'slug': book['slug'],
        'terms': book['terms'],
        'tags': book['tags'],
        'meta': book['meta'],
        'credit': book['credit'],
        'value': book['value'],
        'status': book['status'],
        'creation': book['creation'],
        'updated': book['updated'],
    }


def output_single_book(book):
    output = output_book(book)
    user = g.curr_user
    User = current_app.mongodb.User
    in_stock = current_app.mongodb.BookVolume.count_stocked(book['_id'])
    in_lend = current_app.mongodb.\
        BookVolume.count_lend(user['_id'], book['_id'])
    in_pending = current_app.mongodb.\
        BookVolume.count_pending(user['_id'], book['_id'])
    overlend = current_app.mongodb.BookVolume.check_overlend(user['_id'])
    output.update({
        'activated': user['status'] == User.STATUS_ACTIVATED,
        'overlend': overlend,
        'in_stock': in_stock,
        'in_inventory': in_lend + in_pending,
        'is_afford': user['credit'] > book['credit']
    })
    return output
