# coding=utf-8
from __future__ import absolute_import


from document import BaseDocument, ObjectId, INDEX_DESC
from utils.misc import now


class Media(BaseDocument):
    MAX_QUERY = 120

    structure = {
        'scope': unicode,
        'key': unicode,
        'filename': unicode,
        'mimetype': unicode,
        'size': int,
        'creation': int,
        'updated': int,
    }

    required_fields = ['scope', 'key']

    default_values = {
        'filename': u'',
        'mimetype': u'',
        'size': 0,
        'creation': now,
        'updated': now,
    }

    indexes = [
        {
            'fields': ['key'],
            'unique': True,
        },
        {
            'fields': ['user_id']
        },
        {
            'fields': ['size']
        },
        {
            'fields': ['updated']
        },
    ]

    def find_one_by_id(self, _id):
        return self.find_one({
            '_id': ObjectId(_id)
        })

    def find_one_by_key(self, key):
        return self.find_one({
            'key': key
        })

    def find_all(self):
        return self.find().sort('updated', INDEX_DESC).limit(self.MAX_QUERY)
