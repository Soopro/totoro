# coding=utf-8
from .controllers import *

urlpatterns = [
    # open api
    ('/configure', get_configure, 'GET'),

    ('/book', list_books, 'GET'),
    ('/book/<book_slug>', get_book, 'GET'),

    ('/category', list_terms, 'GET'),
    ('/category/<term_key>', get_term, 'GET'),

]
