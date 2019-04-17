# coding=utf-8
from __future__ import absolute_import


def register_blueprints(app):
    from admin.blueprints.dashboard import blueprint as dashboard_module
    app.register_blueprint(dashboard_module)

    from admin.blueprints.auth import blueprint as auth_module
    app.register_blueprint(auth_module, url_prefix='/auth')

    from admin.blueprints.user import blueprint as user_module
    app.register_blueprint(user_module, url_prefix='/user')

    from admin.blueprints.media import blueprint as media_module
    app.register_blueprint(media_module, url_prefix='/media')

    from admin.blueprints.org import blueprint as org_module
    app.register_blueprint(org_module, url_prefix='/org')

    from admin.blueprints.post import blueprint as post_module
    app.register_blueprint(post_module, url_prefix='/post')

    from admin.blueprints.wechat import blueprint as wechat_module
    app.register_blueprint(wechat_module, url_prefix='/wechat')

    from admin.blueprints.report import blueprint as report_module
    app.register_blueprint(report_module, url_prefix='/report')
