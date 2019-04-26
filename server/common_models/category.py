# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument, ObjectId, INDEX_ASC
from utils.misc import now


class Term(BaseDocument):
    MAX_STORAGE = 120

    structure = {
        'key': unicode,
        'parent': unicode,
        'priority': int,
        'meta': dict,
        'creation': int,
        'updated': int
    }
    sensitive_fields = ['meta']
    required_fields = ['key']

    default_values = {
        'meta': {},
        'parent': u'',
        'priority': 0,
        'creation': now,
        'updated': now,
    }

    indexes = [
        {
            'fields': ['cat_id', 'key'],
            'unique': True,
        },
        {
            'fields': ['cat_id'],
        },
        {
            'fields': ['priority', 'creation'],
        },
        {
            'fields': ['user_id']
        }
    ]

    def find_one_by_key(self, key):
        return self.find_one({
            'key': key,
        })

    def find_one_by_id(self, term_id):
        return self.find_one({
            '_id': ObjectId(term_id),
        })

    def find_all(self, ):
        _sort = [('priority', INDEX_ASC), ('creation', INDEX_ASC)]
        return self.find().sort(_sort).limit(self.MAX_STORAGE)

    def eject_subset(self, parent):
        return self.collection.update({
            'parent': parent
        }, {'$set': {'parent': u''}}, multi=True)

    def count_used(self, cat_id):
        return self.find().count()
