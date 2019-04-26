# coding=utf-8
from __future__ import absolute_import


def register_blueprints(app):
    # users
    from blueprints.user import blueprint as user_module
    app.register_blueprint(user_module, url_prefix='/user')

    # books
    from blueprints.library import blueprint as library_module
    app.register_blueprint(library_module, url_prefix='/library')
