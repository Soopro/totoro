# coding=utf-8
from __future__ import absolute_import

import os
import mimetypes

# register new mimetype
mimetypes.init()
mimetypes.add_type('image/svg+xml', '.svg')
# mimetypes.add_type('text/javascript', '.js')
# text/javascript is obsolete.
# Use application/javascript instead which is default.


# config env
SECRET_KEY = os.getenv('TOTORO_SECRET_KEY', None)
CONFIG_NAME = os.getenv('TOTORO_CONFIG_NAME', None)

MONGO_PORT_27017_TCP_ADDR = os.getenv('MONGO_PORT_27017_TCP_ADDR', None)
MONGO_PORT_27017_TCP_PORT = os.getenv('MONGO_PORT_27017_TCP_PORT', None)

REDIS_PORT_6379_TCP_ADDR = os.getenv('REDIS_PORT_6379_TCP_ADDR', None)
REDIS_PORT_6379_TCP_PORT = os.getenv('REDIS_PORT_6379_TCP_PORT', None)

MONGODB_USER = os.getenv('MONGODB_USER')
MONGODB_PASSWD = os.getenv('MONGODB_PASSWD')

REDIS_PASSWD = os.getenv('REDIS_PASSWD')
