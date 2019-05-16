# coding=utf-8
from __future__ import absolute_import

from mongokit import DocumentMigration


class ConfigMigration(DocumentMigration):
    def allmigration01_rename_time_limit(self):
        self.target = {'borrowing_time_limit': {'$exists': True}}
        if not self.status:
            self.update = {
                '$rename': {
                    'borrowing_time_limit': 'rental_time_limit'
                },
            }
