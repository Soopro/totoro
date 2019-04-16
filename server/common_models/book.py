# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument, ObjectId, INDEX_DESC
from utils.misc import now


class Book(BaseDocument):
    STATUS_DEACTIVATED, STATUS_ACTIVATED = (0, 1)

    MAX_QUERY = 60

    structure = {
        'slug': unicode,
        'tags': [unicode],
        'category': [unicode],
        'qty': int,
        'takeout': 0,
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
        'qty': 0,
        'takeout': 0,
        'rating': 0,
        'meta': {},
        'creation': now,
        'updated': now,
        'status': STATUS_DEACTIVATED,
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

    def find_one_by_id(self, org_id):
        return self.find_one({
            '_id': ObjectId(org_id),
        })

    def find_one_by_slug(self, slug):
        return self.find_one({
            'slug': slug,
        })

    def find_one_activated_by_slug(self, slug):
        return self.find_one({
            'slug': slug,
            'status': self.STATUS_ACTIVATED
        })

    def find_activated(self):
        cursor = self.find({
            'status': self.STATUS_ACTIVATED
        }).sort([('rating', INDEX_DESC), ('updated', INDEX_DESC)])
        return cursor.limit(self.MAX_QUERY)

    def find_deactivated(self):
        return self.find({
            'status': self.STATUS_DEACTIVATED
        }).sort('updated', INDEX_DESC).limit(self.MAX_QUERY)

    def count_used(self):
        return self.find({
            'status': self.STATUS_ACTIVATED
        }).count()
