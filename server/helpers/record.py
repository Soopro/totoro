# coding=utf-8
from __future__ import absolute_import

from flask import current_app


def recording(book, volume, user, checkin=False):
    try:
        _recording(book, volume, user, checkin)
    except Exception as e:
        current_app.logger.warn(e)


def _recording(book, volume, user):
    BookRecord = current_app.mongodb.BookRecord
    record = BookRecord()
    record['user_id'] = user['_id']
    record['book_id'] = book['_id']
    record['scope'] = book['slug']
    record['volume'] = u''.format(book['slug'], volume['code'])
    record['customer'] = user['login']
    record['meta'] = {
        'title': book['meta'].get('title') or u'-',
        'customer': user['meta'].get('name') or user['login']
    }
    record.save()
    return record
