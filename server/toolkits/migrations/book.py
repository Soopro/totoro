# coding=utf-8
from __future__ import absolute_import

from mongokit import DocumentMigration


class BookMigration(DocumentMigration):

    # def allmigration01_rename_figure(self):
    #     self.target = {'meta.cover_src': {'$exists': True}}
    #     if not self.status:
    #         self.update = {
    #             '$rename': {
    #                 'meta.cover_src': 'meta.figure'
    #             },
    #         }

    def allmigration01_change_value(self):
        if not self.status:
            for doc in self.collection.find():
                self.target = {'_id': doc['_id']}
                self.update = {
                    '$set': {
                        'value': unicode(doc['value']),
                    },
                }
                self.collection.update(self.target,
                                       self.update,
                                       multi=True,
                                       safe=True)
                print 'change value:', doc['slug']


class BookVolumeMigration(DocumentMigration):
    def allmigration01_rename_rental_time(self):
        self.target = {'borrowing_time': {'$exists': True}}
        if not self.status:
            self.update = {
                '$rename': {
                    'borrowing_time': 'rental_time'
                },
            }

    def allmigration01_rename_renter(self):
        self.target = {'borrower': {'$exists': True}}
        if not self.status:
            self.update = {
                '$rename': {
                    'borrower': 'renter'
                },
            }
