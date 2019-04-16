# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument


class Configuration(BaseDocument):

    structure = {
        'mina_app_id': unicode,
        'mina_app_secret': unicode,
        'admin_code_hash': unicode,
    }
    default_values = {
        'mina_app_id': u'',
        'mina_app_secret': u'',
        'admin_code_hash': u'',
    }
    required_fields = ['admin_code_hash']
