# coding=utf-8
from __future__ import absolute_import

from config import config
from .helpers import connect_mongodb

from .migrations import *


def migration(cfg_type='default'):
    print '-----------------'
    print 'Migration: {}'.format(cfg_type)
    print '-----------------'
    cfg = config.get(cfg_type)
    if not cfg:
        return None

    mongodb_conn, mongodb = connect_mongodb(cfg)

    # users
    UserMigration(mongodb.User).\
        migrate_all(collection=mongodb.User.collection)

    # book
    BookMigration(mongodb.Book).\
        migrate_all(collection=mongodb.Book.collection)

    BookVolumeMigration(mongodb.BookVolume).\
        migrate_all(collection=mongodb.BookVolume.collection)

    return True
