# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument, ObjectId, INDEX_DESC
from utils.misc import now, parse_int


class Book(BaseDocument):
    STATUS_OFFLINE, STATUS_ONLINE = (0, 1)

    MAX_QUERY = 60

    structure = {
        'slug': unicode,
        'tags': [unicode],
        'terms': [unicode],
        'credit': int,
        'rating': int,
        'value': unicode,
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
        'rating': 0,
        'value': u'',
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

    def find_activated(self, term=None, timestamp=None):
        _query = {
            'status': self.STATUS_ONLINE
        }
        if term:
            _query.update({'terms': term})
        _query = self._attach_timestamp(_query, timestamp)
        cursor = self.find(_query).sort([('rating', INDEX_DESC),
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
        return self.find().sort('creation', INDEX_DESC)

    def search(self, keys, timestamp=None):
        _query = {
            '_keywords': {'$all': [k.lower() for k in keys if k]}
        }
        _query = self._attach_timestamp(_query, timestamp)
        cursor = self.find(_query).sort('creation', INDEX_DESC)
        return cursor.limit(self.MAX_QUERY)

    def count_used(self):
        return self.find().count()

    # override
    def save(self, *args, **kwargs):
        tags = [tag.strip().lower() for tag in self['tags']]
        slug_keys = [self['slug']] + self['slug'].split('-')
        self['_keywords'] = list(set(slug_keys + tags))
        return super(Book, self).save(*args, **kwargs)

    # helpers
    def _attach_timestamp(self, find_query, timestamp):
        # use to prevent duplicate entries when pagination
        if not timestamp:
            return find_query
        find_query.update({
            'updated': {'$lt': parse_int(timestamp)}
        })
        return find_query


class BookVolume(BaseDocument):
    STATUS_PENDING, STATUS_STOCK, STATUS_LEND = 0, 1, 2

    MAX_QUERY = 60
    MAX_LEND = 6

    structure = {
        'book_id': ObjectId,
        'user_id': ObjectId,
        'scope': unicode,
        'code': unicode,
        'renter': unicode,  # renter address
        'rental_time': int,  # timestamp of the time rented
        'meta': dict,  # a copy of book meta
        'status': int,
        'creation': int,
        'updated': int,
    }
    required_fields = ['book_id', 'scope', 'code']
    default_values = {
        'user_id': None,
        'renter': u'',
        'rental_time': 0,
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
            'fields': ['rental_time'],
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

    def find_one_lend_by_bookid_uid(self, book_id, user_id):
        return self.find_one({
            'book_id': ObjectId(book_id),
            'user_id': ObjectId(user_id),
            'status': self.STATUS_STOCK,
        })

    def find_one_pending_by_bookid_uid(self, book_id, user_id):
        return self.find_one({
            'book_id': ObjectId(book_id),
            'user_id': ObjectId(user_id),
            'status': self.STATUS_PENDING,
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

    def find_pending(self):
        return self.find({
            'status': self.STATUS_PENDING,
        }).sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def find_overtime(self, duration=2592000):
        query = {
            'status': self.STATUS_LEND,
        }
        if duration:
            query.update({
                'rental_time': {
                    '$ne': 0,
                    '$lt': now() - duration,
                }
            })
        cursor = self.find(query).sort('updated', INDEX_DESC)
        return cursor.limit(self.MAX_QUERY)

    def find_all(self):
        return self.find().sort('book_id', INDEX_DESC)

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

    def count_lend(self, user_id=None, book_id=None):
        _query = {
            'status': self.STATUS_LEND
        }
        if user_id:
            _query.update({
                'user_id': ObjectId(user_id)
            })
        if book_id:
            _query.update({
                'book_id': ObjectId(book_id),
            })
        return self.find(_query).count()

    def count_pending(self, user_id=None, book_id=None):
        _query = {
            'status': self.STATUS_PENDING
        }
        if user_id:
            _query.update({
                'user_id': ObjectId(user_id)
            })
        if book_id:
            _query.update({
                'book_id': ObjectId(book_id),
            })
        return self.find(_query).count()

    def check_overlend(self, user_id):
        lend_count = self.find({
            'user_id': ObjectId(user_id),
            'status': self.STATUS_LEND
        }).count()
        return lend_count >= self.MAX_LEND


class BookRecord(BaseDocument):
    MAX_QUERY = 60

    structure = {
        'user_id': ObjectId,
        'book_id': ObjectId,
        'scope': unicode,  # book slug
        'volume': unicode,  # volume code
        'customer': unicode,  # user login
        'meta': dict,
        'creation': int,
        'updated': int,
    }
    sensitive_fields = ['meta']
    required_fields = ['user_id', 'book_id', 'scope', 'volume', 'customer']
    default_values = {
        'meta': {},
        'creation': now,
        'updated': now,
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
        return self.find().sort('updated', INDEX_DESC)

    def count_used(self):
        return self.find().count()
