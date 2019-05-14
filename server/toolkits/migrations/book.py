# coding=utf-8
from __future__ import absolute_import

from mongokit import DocumentMigration


class BookMigration(DocumentMigration):
    pass
    # def allmigration01_rename_figure(self):
    #     self.target = {'meta.cover_src': {'$exists': True}}
    #     if not self.status:
    #         self.update = {
    #             '$rename': {
    #                 'meta.cover_src': 'meta.figure'
    #             },
    #         }

    # def allmigration01_refine_keywords(self):
    #     if not self.status:
    #         for doc in self.collection.find():
    #             slug_keys = [doc['slug']] + doc['slug'].split('-')
    #             keywords = list(set(slug_keys))
    #             self.target = {'_id': doc['_id']}
    #             self.update = {
    #                 '$set': {
    #                     '_keywords': keywords,
    #                 },
    #             }
    #             self.collection.update(self.target,
    #                                    self.update,
    #                                    multi=True,
    #                                    safe=True)
    #             print 'refine keywords:', doc['slug'], slug_keys


class BookVolumeMigration(DocumentMigration):
    pass
    # def allmigration01_rename_figure(self):
    #     self.target = {'meta.cover_src': {'$exists': True}}
    #     if not self.status:
    #         self.update = {
    #             '$rename': {
    #                 'meta.cover_src': 'meta.figure'
    #             },
    #         }
