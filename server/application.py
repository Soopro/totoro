# coding=utf-8
from __future__ import absolute_import

from flask import Flask, request, g, current_app, send_from_directory
from redis import ConnectionPool, Redis
from mongokit import Connection as MongodbConn

import traceback
import logging
from logging.handlers import RotatingFileHandler

from utils.encoders import Encoder
from utils.files import ensure_dirs
from utils.response import make_json_response, make_cors_headers

from apiresps.errors import (APIError,
                             NotFound,
                             Unauthorized,
                             PermissionDenied,
                             MethodNotAllowed,
                             BadRequest,
                             UncaughtException)

from common_models import (User, Book, BookVolume, BookRecord, Term,
                           Media, Notify, Configuration)

from blueprints import register_blueprints

from config import config
import envs

__version_info__ = ('0', '2', '0')
__version__ = '.'.join(__version_info__)


__maker__ = {
    'creator': ['Redyyu']
}


def create_app(config_name='default'):
    config_name = envs.CONFIG_NAME or config_name

    app = Flask(__name__)

    app.version = __version__
    app.maker = __maker__

    # config
    app.config.from_object(config[config_name])
    app.debug = app.config.get('DEBUG')
    app.json_encoder = Encoder

    ensure_dirs(
        app.config.get('LOG_FOLDER'),
        app.config.get('TEMPORARY_FOLDER'),
        app.config.get('UPLOADS_FOLDER')
    )

    # logging
    if app.config.get('UNITTEST') is True:
        app.logger.setLevel(logging.FATAL)
    else:
        error_file_handler = RotatingFileHandler(
            app.config.get('LOGGING')['error']['file'],
            maxBytes=app.config.get('LOGGING_ROTATING_MAX_BYTES'),
            backupCount=app.config.get('LOGGING_ROTATING_BACKUP_COUNT')
        )

        error_file_handler.setLevel(logging.WARNING)
        error_file_handler.setFormatter(
            logging.Formatter(app.config.get('LOGGING')['error']['format'])
        )

        info_file_handler = RotatingFileHandler(
            app.config.get('LOGGING')['info']['file'],
            maxBytes=app.config.get('LOGGING_ROTATING_MAX_BYTES'),
            backupCount=app.config.get('LOGGING_ROTATING_BACKUP_COUNT')
        )
        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(logging.Formatter(
            app.config.get('LOGGING')['info']['format']
        ))
        app.logger.addHandler(error_file_handler)
        app.logger.addHandler(info_file_handler)

    # database connections
    rds_pool = ConnectionPool(host=app.config.get('REDIS_HOST'),
                              port=app.config.get('REDIS_PORT'),
                              db=app.config.get('REDIS_DB'),
                              password=app.config.get('REDIS_PASSWORD'))
    rds_conn = Redis(connection_pool=rds_pool)

    mongodb_conn = MongodbConn(
        host=app.config.get('MONGODB_HOST'),
        port=app.config.get('MONGODB_PORT'),
        max_pool_size=app.config.get('MONGODB_MAX_POOL_SIZE')
    )
    mongodb = mongodb_conn[app.config.get('MONGODB_DATABASE')]
    mongodb_user = app.config.get('MONGODB_USER')
    mongodb_pwd = app.config.get('MONGODB_PASSWORD')
    if mongodb_user and mongodb_pwd:
        mongodb.authenticate(mongodb_user, mongodb_pwd)

    # register mongokit models
    mongodb_conn.register([User, Book, BookVolume, BookRecord, Term,
                           Media, Notify, Configuration])

    # inject database connections to app object
    app.redis = rds_conn
    app.mongodb_conn = mongodb_conn
    app.mongodb = mongodb

    # register error handlers
    @app.errorhandler(400)
    def app_error_400(error):
        return make_json_response(BadRequest(repr(error)))

    @app.errorhandler(401)
    def app_error_401(error):
        # Unauthorized but not raised by API
        current_app.logger.warn(error)
        return make_json_response(Unauthorized(error))

    @app.errorhandler(403)
    def app_error_403(error):
        return make_json_response(PermissionDenied(error))

    @app.errorhandler(404)
    def app_error_404(error):
        return make_json_response(NotFound(repr(error)))

    @app.errorhandler(405)
    def app_error_405(error):
        return make_json_response(MethodNotAllowed(repr(error)))

    @app.errorhandler(APIError)
    def app_api_error(error):
        return make_json_response(error)

    if app.config.get('UNITTEST') is not True:
        @app.errorhandler(Exception)
        def app_error_uncaught(error):
            current_app.logger.error(
                'Uncaught Exception: {}\n{}'.format(repr(error),
                                                    traceback.format_exc())
            )
            return make_json_response(UncaughtException(repr(error)))

    # register before request handlers
    @app.before_request
    def app_before_request():
        # cors response
        if request.method == 'OPTIONS':
            resp = current_app.make_default_options_response()
            cors_headers = make_cors_headers()
            resp.headers.extend(cors_headers)
            return resp
        else:
            configure = current_app.mongodb.Configuration.get_conf() or {}
            if not configure:
                raise PermissionDenied('configure')
            g.configure = configure

    # uploads
    @app.route('{}/<path:filepath>'.format(app.config['UPLOADS_URL_PATH']))
    def send_file(filepath):
        return send_from_directory(app.config['UPLOADS_FOLDER'], filepath)

    # register blueprints
    register_blueprints(app)

    print '-------------------------------------------------------'
    print 'Totoro: {}'.format(app.version)
    print 'Creators: {}'.format(', '.join(app.maker['creator']))
    print '-------------------------------------------------------'

    return app
