# coding=utf-8
from __future__ import absolute_import

from apiresps.errors import NotFound


class BookNotFound(NotFound):
    response_code = 500001
    status_message = 'BOOK_NOT_FOUND'


class BookNotEnoughVolume(NotFound):
    response_code = 500002
    status_message = 'BOOK_NOT_ENOUGH_VOLUME'


class BookNotEnoughCredit(NotFound):
    response_code = 500003
    status_message = 'BOOK_NOT_ENOUGH_CREDIT'


class BookReachRentLimit(NotFound):
    response_code = 500004
    status_message = 'BOOK_REACH_RENT_LIMIT'


class CategoryNotFound(NotFound):
    response_code = 500101
    status_message = 'CATEGORY_NOT_FOUND'
