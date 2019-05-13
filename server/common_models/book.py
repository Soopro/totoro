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
        'terms': [unicode],
        'credit': int,
        'value': int,
        'rating': int,
        '_keywords': [unicode],
        'meta': dict,
        'memo': unicode,
        'status': int,
        'creation': int,
        'updated': int,
    }
    sensitive_fields = ['meta']
    required_fields = ['slug']
    default_values = {
        'tags': [],
        'terms': [],
        'credit': 0,
        'value': 0,
        'rating': 0,
        '_keywords': [],
        'meta': {},
        'memo': u'',
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
            'fields': ['terms'],
        },
        {
            'fields': ['tags'],
        },
        {
            'fields': ['_keywords'],
        },
        {
            'fields': ['rating', 'creation'],
        },
        {
            'fields': ['creation'],
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

    def find_activated(self, term=None):
        query = {
            'status': self.STATUS_ONLINE
        }
        if term:
            query.update({'terms': term})
        cursor = self.find(query).sort([('rating', INDEX_DESC),
                                        ('creation', INDEX_DESC)])
        return cursor.limit(self.MAX_QUERY)

    def find_by_ids(self, id_list):
        return self.find({
            '_id': {
                '$in': [ObjectId(_id) for _id in id_list[:self.MAX_QUERY]
                        if ObjectId.is_valid(_id)]
            },
        }).limit(self.MAX_QUERY)

    def find_all(self):
        return self.find().sort('creation', INDEX_DESC).limit(self.MAX_QUERY)

    def search(self, keys):
        return self.find({
            '_keywords': {'$all': [k.lower() for k in keys if k]}
        }).sort('creation', INDEX_DESC).limit(self.MAX_QUERY)

    def count_used(self):
        return self.find().count()

    # override
    def save(self, *args, **kwargs):
        tags = [tag.strip().lower() for tag in self['tags']]
        self['_keywords'] = list(set([self['slug']] + tags))
        return super(Book, self).save(*args, **kwargs)


class BookVolume(BaseDocument):
    STATUS_PENDING, STATUS_STOCK, STATUS_LEND = 0, 1, 2

    MAX_QUERY = 60

    structure = {
        'book_id': ObjectId,
        'user_id': ObjectId,
        'scope': unicode,
        'code': unicode,
        'borrower': unicode,  # user login
        'borrowing_time': int,  # timestamp for the time borrowing
        'meta': dict,  # a copy of book meta
        'status': int,
        'creation': int,
        'updated': int,
    }
    required_fields = ['book_id', 'scope', 'code']
    default_values = {
        'user_id': None,
        'borrower': u'',
        'borrowing_time': 0,
        'meta': {},
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
            'fields': ['user_id', 'status'],
        },
        {
            'fields': ['borrowing_time'],
        },
        {
            'fields': ['user_id'],
        },
        {
            'fields': ['book_id'],
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

    def find_one_stocked_by_bookid(self, book_id):
        return self.find_one({
            'book_id': ObjectId(book_id),
            'status': self.STATUS_STOCK,
        })

    def find_by_bookid(self, book_id):
        return self.find({
            'book_id': ObjectId(book_id),
        }).sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def find_stocked_by_bookid(self, book_id):
        return self.find({
            'book_id': ObjectId(book_id),
            'status': self.STATUS_STOCK,
        }).sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def find_lend_by_uid(self, user_id):
        return self.find({
            'user_id': ObjectId(user_id),
            'status': self.STATUS_LEND,
        }).sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def find_pending_by_uid(self, user_id):
        return self.find({
            'user_id': ObjectId(user_id),
            'status': self.STATUS_PENDING,
        }).sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def find_overtime(self, duration=2592000):
        query = {
            'status': self.STATUS_LEND,
        }
        if duration:
            query.update({
                'borrowing_time': {
                    '$ne': 0,
                    '$lt': now() - duration,
                }
            })
        cursor = self.find(query).sort('updated', INDEX_DESC)
        return cursor.limit(self.MAX_QUERY)

    def find_all(self):
        return self.find().sort('book_id', INDEX_DESC).limit(self.MAX_QUERY)

    def refresh_meta(self, book_id, scope, meta):
        # login can on exists once.
        return self.collection.update(
            {'book_id': ObjectId(book_id)},
            {'$set': {'scope': scope, 'meta': meta}}, multi=True)

    def count_used(self, book_id):
        return self.find({
            'book_id': ObjectId(book_id),
        }).count()

    def count_stocked(self, book_id):
        return self.find({
            'book_id': ObjectId(book_id),
            'status': self.STATUS_STOCK
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
