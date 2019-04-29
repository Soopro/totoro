# coding=utf-8
from .controllers import *

urlpatterns = [
    # open api
    ('/login', login, 'POST'),

    # member
    ('/join', join_member, 'POST'),

    # profile
    ('/profile', get_profile, 'GET'),
    ('/profile', update_profile, 'PUT'),

    # inventory
    ('/inventory/book', list_volumes, 'GET'),
    ('/inventory/records', list_records, 'GET'),

]
