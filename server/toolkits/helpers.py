# coding=utf-8
from __future__ import absolute_import

from document import MongodbConn

from common_models import (User, Book, BookRecord, BookVolume, Term, Media)


models = [
    User, Book, BookRecord, BookVolume, Term, Media
]


def connect_mongodb(cfg):
    mongodb_conn = MongodbConn(
        host=cfg.MONGODB_HOST,
        port=cfg.MONGODB_PORT,
        max_pool_size=cfg.MONGODB_MAX_POOL_SIZE,
    )

    mongodb_conn.register(models)

    mongodb = mongodb_conn[cfg.MONGODB_DATABASE]
    if cfg.MONGODB_USER and cfg.MONGODB_PASSWD:
        mongodb.authenticate(cfg.MONGODB_USER, cfg.MONGODB_PASSWD)

    return mongodb_conn, mongodb
