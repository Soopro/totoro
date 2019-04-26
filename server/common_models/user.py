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
        'meta': dict,
        'creation': int,
        'updated': int,
        'status': int,
    }
    sensitive_fields = ['meta']
    required_fields = ['openid']
    default_values = {
        'login': u'',
        'password_hash': u'',
        'unionid': u'',
        'meta': {},
        'creation': now,
        'updated': now,
        'status': STATUS_DEACTIVATED
    }
    indexes = [
        {
            'fields': ['openid'],
            'unique': True,
        },
        {
            'fields': ['login'],
            'unique': True,
        },
        {
            'fields': ['creation'],
        },
        {
            'fields': ['status'],
        }
    ]

    def find_all(self):
        return self.find().sort('creation', INDEX_DESC).limit(self.MAX_QUERY)

    def find_activated(self):
        return self.find({
            'status': self.STATUS_ACTIVATED
        }).sort('creation', INDEX_DESC).limit(self.MAX_QUERY)

    def find_by_status(self, status):
        return self.find({
            'status': status
        }).sort('creation', INDEX_DESC).limit(self.MAX_QUERY)

    def find_one_by_id(self, user_id):
        return self.find_one({
            '_id': ObjectId(user_id),
        })

    def find_one_by_login(self, login):
        return self.find_one({
            'login': login,
        })

    def find_one_by_openid(self, openid):
        return self.find_one({
            'openid': openid,
        })

    def displace_login(self, login, openid):
        # login can on exists once.
        return self.collection.update(
            {'openid': {'$ne': openid}, 'login': login},
            {'$set': {'login': u'', 'status': self.STATUS_DEACTIVATED}},
            multi=True)

    def count_used(self):
        return self.find().count()
