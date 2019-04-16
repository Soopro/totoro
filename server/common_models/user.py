# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument, ObjectId, INDEX_DESC
from utils.misc import now


class User(BaseDocument):
    STATUS_DEACTIVATED, STATUS_ACTIVATED, STATUS_BANNED = (0, 1, 2)

    MAX_QUERY = 120

    structure = {
        'login': unicode,
        'password_hash': unicode,
        'openid': unicode,
        'unionid': unicode,
        'subscribed': bool,
        'meta': dict,
        'creation': int,
        'updated': int,
        'deleted': int,
        'status': int,
    }
    sensitive_fields = ['meta']
    required_fields = ['login', 'openid', 'password_hash']
    default_values = {
        'unionid': u'',
        'subscribed': False,
        'meta': {},
        'creation': now,
        'updated': now,
        'deleted': 0,
        'status': STATUS_DEACTIVATED
    }
    indexes = [
        {
            'fields': ['creation'],
        },
        {
            'fields': ['deleted'],
        }
    ]

    def find_alive(self):
        return self.find({
            'deleted': 0,
        }).sort('creation', INDEX_DESC).limit(self.MAX_QUERY)

    def find_dead(self):
        return self.find({
            'deleted': 1,
        }).sort('creation', INDEX_DESC).limit(self.MAX_QUERY)

    def find_one_by_id(self, user_id):
        return self.find_one({
            '_id': ObjectId(user_id),
            'deleted': 0,
        })

    def find_one_by_login(self, login):
        return self.find_one({
            'login': login,
            'deleted': 0,
        })

    def find_one_dead_by_id(self, user_id):
        return self.find_one({
            '_id': ObjectId(user_id),
            'deleted': 1,
        })

    def count_used(self):
        return self.find({
            'deleted': 0,
        }).count()

    def remove(self):
        self['updated'] = now()
        self['deleted'] = 1
        self.save()
        return self['_id']
