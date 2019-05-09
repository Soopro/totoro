# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument
from utils.misc import now


class Configuration(BaseDocument):

    structure = {
        'mina_app_id': unicode,
        'mina_app_secret': unicode,
        'passcode_hash': unicode,
        'meta': dict,
        'borrowing_time_limit': int,
        'creation': int,
        'updated': int
    }
    default_values = {
        'mina_app_id': u'',
        'mina_app_secret': u'',
        'passcode_hash': u'',
        'meta': {},
        'borrowing_time_limit': 0,
        'creation': now,
        'updated': now
    }
    sensitive_fields = ['meta']
    required_fields = ['passcode_hash']

    def get_conf(self):
        return self.find_one({
            'passcode_hash': {'$ne': u''}
        })

    def clear_conf(self):
        return self.collection.remove({})
