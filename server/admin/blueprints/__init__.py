# coding=utf-8
from __future__ import absolute_import


def register_blueprints(app):
    from admin.blueprints.dashboard import blueprint as dashboard_module
    app.register_blueprint(dashboard_module)

    from admin.blueprints.gate import blueprint as gate_module
    app.register_blueprint(gate_module, url_prefix='/gate')

    from admin.blueprints.user import blueprint as user_module
    app.register_blueprint(user_module, url_prefix='/user')

    from admin.blueprints.media import blueprint as media_module
    app.register_blueprint(media_module, url_prefix='/media')
