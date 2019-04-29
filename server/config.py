# coding=utf-8
from __future__ import absolute_import

from datetime import timedelta
import os
import envs


class Config(object):

    # env
    DEBUG = True
    SECRET_KEY = 'secret_totoro_.<OgTfdw[6@uk">)CRL#Vy*DiD)cfK#B8Bv}M>'

    # path
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DEPLOY_DIR = os.path.join(BASE_DIR, 'deployment_data')

    LOG_FOLDER = os.path.join(DEPLOY_DIR, 'log')
    TEMPORARY_FOLDER = os.path.join(DEPLOY_DIR, 'tmp')
    UPLOADS_FOLDER = os.path.join(DEPLOY_DIR, 'uploads')

    # url
    ALLOW_ORIGINS = ['*']
    ALLOW_CREDENTIALS = False
    DENIED_ORIGINS = []

    UPLOADS_URL_PATH = '/uploads'
    UPLOADS_URL = 'http://localhost:9000{}'.format(UPLOADS_URL_PATH)

    # analytics
    ONLINE_LAST_MINUTES = 30

    # content limit
    MAX_CONTENT_LENGTH = 24 * 1024 * 1024

    # file uploads
    ALLOWED_MEDIA_EXTS = ('jpg', 'jpeg', 'png', 'gif')

    # JWT
    JWT_SECRET_KEY = SECRET_KEY  # SECRET_KEY
    JWT_ALGORITHM = 'HS256'
    JWT_VERIFY_EXPIRATION = True,
    JWT_LEEWAY = 60
    JWT_EXPIRATION_DELTA = timedelta(seconds=3600 * 24 * 30)
    JWT_AUTH_HEADER_KEY = 'Authorization'
    JWT_AUTH_HEADER_PREFIX = 'Bearer'

    # expirations
    REGISTER_EXPIRATION = 3600 * 3
    RESET_PWD_EXPIRATION = 3600 * 3

    # mongodb
    MONGODB_HOST = envs.MONGO_PORT_27017_TCP_ADDR or 'localhost'
    MONGODB_PORT = int(envs.MONGO_PORT_27017_TCP_PORT or 27017)
    MONGODB_MAX_POOL_SIZE = 10
    MONGODB_USER = envs.MONGODB_USER
    MONGODB_PASSWD = envs.MONGODB_PASSWD

    # redis
    REDIS_PASSWD = envs.REDIS_PASSWD
    REDIS_HOST = envs.REDIS_PORT_6379_TCP_ADDR or '127.0.0.1'
    REDIS_PORT = int(envs.REDIS_PORT_6379_TCP_PORT or 6379)
    REDIS_DB = 0


class DevelopmentConfig(Config):
    # mongodb
    MONGODB_DATABASE = 'dev_totoro'


class TestCaseConfig(Config):
    UNITTEST = True
    SECRET_KEY = 'secret'
    MONGODB_DATABASE = 'test_totoro'


class TestingConfig(Config):
    # base
    DEPLOY_DIR = '/data/deployment_data/totoro'
    LOG_FOLDER = os.path.join(DEPLOY_DIR, 'log')
    TEMPORARY_FOLDER = os.path.join(DEPLOY_DIR, 'tmp')

    # mongodb
    MONGODB_DATABASE = 'totoro'


class ProductionConfig(Config):
    # base
    DEBUG = False
    DENY_PUBLIC_ACCESS = True
    SEND_MAIL = True

    DEPLOY_DIR = '/data/totoro/deployment_data'
    LOG_FOLDER = os.path.join(DEPLOY_DIR, 'log')
    TEMPORARY_FOLDER = os.path.join(DEPLOY_DIR, 'tmp')
    UPLOADS_FOLDER = os.path.join(DEPLOY_DIR, 'uploads')

    # mongodb
    MONGODB_DATABASE = 'totoro'
    MONGODB_USER = None
    MONGODB_PASSWORD = None

    # redis
    REDIS_PASSWORD = None


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'testcase': TestCaseConfig,
    'default': DevelopmentConfig
}
