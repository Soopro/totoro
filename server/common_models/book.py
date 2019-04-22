# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument, ObjectId, INDEX_DESC
from utils.misc import now


class Book(BaseDocument):
    STATUS_OFFLINE, STATUS_ONLINE = (0, 1)

    MAX_QUERY = 60

    structure = {
        'slug': unicode,
        'tags': [unicode],
        'category': [unicode],
        'rating': int,
        'meta': dict,
        'status': int,
        'creation': int,
        'updated': int,
    }
    sensitive_fields = ['meta']
    required_fields = ['slug']
    default_values = {
        'tags': [],
        'category': [],
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
        return self.find().count()


class BookVolume(BaseDocument):
    STATUS_STOCK, STATUS_LEND = (0, 1)

    MAX_QUERY = 60

    structure = {
        'book_id': ObjectId,
        'user_id': ObjectId,
        'serial_number': unicode,
        'code': unicode,
        'borrower': unicode,  # user login
        'status': int,
        'creation': int,
        'updated': int,
    }
    required_fields = ['book_id', 'serial_number', 'code']
    default_values = {
        'user_id': None,
        'borrower': u'',
        'creation': now,
        'updated': now,
        'status': STATUS_STOCK,
    }
    indexes = [
        {
            'fields': ['book_id', 'code'],
            'unique': True,
        },
        {
            'fields': ['updated'],
        }
    ]

    def find_one_by_id(self, volume_id):
        return self.find_one({
            '_id': ObjectId(volume_id),
        })

    def find_one_by_bookid_id(self, book_id, volume_id):
        return self.find_one({
            '_id': ObjectId(volume_id),
            'book_id': ObjectId(book_id),
        })

    def find_one_by_bookid_code(self, book_id, code):
        return self.find_one({
            'book_id': ObjectId(book_id),
            'code': code,
        })

    def find_by_bookid(self, book_id):
        return self.find({
            'book_id': ObjectId(book_id),
        }).sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def count_used(self, book_id):
        return self.find({
            'book_id': ObjectId(book_id),
        }).count()


class BookRecord(BaseDocument):
    STATUS_CHECKIN, STATUS_CHECKOUT = (0, 1)

    MAX_QUERY = 60

    structure = {
        'book_id': ObjectId,
        'user_id': ObjectId,
        'volume': unicode,  # volume code
        'borrower': unicode,  # user login
        'meta': dict,
        'status': int,
        'creation': int,
        'updated': int,
    }
    sensitive_fields = ['meta']
    required_fields = ['book_id', 'user_id', 'volume']
    default_values = {
        'borrower': u'',
        'meta': {},
        'creation': now,
        'updated': now,
        'status': STATUS_CHECKIN,
    }
    indexes = [
        {
            'fields': ['book_id'],
        },
        {
            'fields': ['user_id'],
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
        return self.find({
            'book_id': ObjectId(book_id),
        }).sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def find_by_uid(self, user_id):
        return self.find({
            'user_id': ObjectId(user_id),
        }).sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def find_all(self):
        return self.find().sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def count_used(self):
        return self.find().count()
