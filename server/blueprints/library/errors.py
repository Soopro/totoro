# coding=utf-8
from __future__ import absolute_import

from apiresps.errors import NotFound


class BookNotFound(NotFound):
    response_code = 500001
    status_message = 'BOOK_NOT_FOUND'


class CategoryNotFound(NotFound):
    response_code = 500101
    status_message = 'CATEGORY_NOT_FOUND'
