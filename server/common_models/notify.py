# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument, ObjectId


class Notify(BaseDocument):
    structure = {
        'slug': unicode,
        'template_id': unicode,
        'source': unicode,
        'params': dict,
    }
    required_fields = ['slug', 'template_id']
    default_values = {
        'params': {},
    }
    indexes = [
        {
            'fields': ['slug'],
            'unique': True,
        },
    ]

    def find_one_by_id(self, _id):
        return self.find_one({
            '_id': ObjectId(_id),
        })

    def find_one_by_slug(self, slug):
        return self.find_one({
            'slug': slug
        })

    def find_all(self):
        return self.find()
