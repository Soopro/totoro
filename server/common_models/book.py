# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument, ObjectId, INDEX_DESC
from utils.misc import now


class Book(BaseDocument):
    STATUS_OFFLINE, STATUS_ONLINE = (0, 1)

    MAX_QUERY = 60

    structure = {
        'slug': unicode,
        'code': unicode,
        'tags': [unicode],
        'category': [unicode],
        'volumes': [unicode],
        'rating': int,
        'meta': dict,
        'status': int,
        'creation': int,
        'updated': int,
    }
    sensitive_fields = ['meta']
    required_fields = ['slug', 'code']
    default_values = {
        'tags': [],
        'category': [],
        'volumes': [],
        'rating': 0,
        'meta': {},
        'creation': now,
        'updated': now,
        'status': STATUS_OFFLINE,
    }
    indexes = [
        {
            'fields': ['slug'],
            'unique': True,
        },
        {
            'fields': ['code'],
            'unique': True,
        },
        {
            'fields': ['category'],
        },
        {
            'fields': ['tags'],
        },
        {
            'fields': ['rating', 'updated'],
        },
        {
            'fields': ['updated'],
        }
    ]

    def find_one_by_id(self, book_id):
        return self.find_one({
            '_id': ObjectId(book_id),
        })

    def find_one_by_slug(self, slug):
        return self.find_one({
            'slug': slug,
        })

    def find_one_activated_by_slug(self, slug):
        return self.find_one({
            'slug': slug,
            'status': self.STATUS_ONLINE
        })

    def find_activated(self):
        cursor = self.find({
            'status': self.STATUS_ONLINE
        }).sort([('rating', INDEX_DESC), ('updated', INDEX_DESC)])
        return cursor.limit(self.MAX_QUERY)

    def find_all(self):
        return self.find().sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def count_used(self):
        return self.find({
            'status': self.STATUS_ACTIVATED
        }).count()


class Record(BaseDocument):
    STATUS_STOCK, STATUS_LEND = (0, 1)

    MAX_QUERY = 60

    structure = {
        'book_id': ObjectId,
        'user_id': [unicode],
        'meta': dict,
        'volume': unicode,
        'status': int,
        'date_borrowing': unicode,
        'date_returning': unicode,
        'creation': int,
        'updated': int,
    }
    sensitive_fields = ['meta']
    required_fields = ['book_id', 'user_id']
    default_values = {
        'volume': u'',
        'meta': {},
        'date_borrowing': u'',
        'date_returning': u'',
        'creation': now,
        'updated': now,
        'status': STATUS_STOCK,
    }
    indexes = [
        {
            'fields': ['book_id'],
        },
        {
            'fields': ['user_id'],
        },
        {
            'fields': ['date_borrowing'],
        },
        {
            'fields': ['date_returning'],
        },
        {
            'fields': ['updated'],
        }
    ]

    def find_one_by_id(self, _id):
        return self.find_one({
            '_id': ObjectId(_id),
        })

    def find_by_bookid(self, book_id):
        return self.find_one({
            'book_id': ObjectId(book_id),
        })

    def find_by_uid(self, user_id):
        return self.find_one({
            'user_id': ObjectId(user_id),
        })

    def find_all_lend(self):
        cursor = self.find({
            'status': self.STATUS_LEND
        }).sort('updated', INDEX_DESC)
        return cursor.limit(self.MAX_QUERY)

    def find_all(self):
        return self.find().sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def count_used(self):
        return self.find({
            'status': self.STATUS_ACTIVATED
        }).count()
