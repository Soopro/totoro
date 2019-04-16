# coding=utf-8
from __future__ import absolute_import


def register_blueprints(app):
    from blueprints.user import blueprint as user_module
    app.register_blueprint(user_module, url_prefix='/user')

    from blueprints.media import blueprint as media_module
    app.register_blueprint(media_module, url_prefix='/media')

    from blueprints.area import blueprint as area_module
    app.register_blueprint(area_module, url_prefix='/area')

    from blueprints.event import blueprint as event_module
    app.register_blueprint(event_module, url_prefix='/event')
