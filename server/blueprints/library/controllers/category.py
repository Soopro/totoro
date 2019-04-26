# coding=utf-8
from __future__ import absolute_import

from flask import current_app

from utils.response import output_json

from .erros import CategoryNotFound


@output_json
def list_terms():
    cates = current_app.mongodb.Category.find_all()
    return [output_cate(cat) for cat in cates]


@output_json
def get_term(term_key):
    cate = current_app.mongodb.Category.find_one_by_key(term_key)
    if not cate:
        raise CategoryNotFound
    return output_cate(cate)


# outputs
def output_cate(cate):
    return {
        'id': cate['_id'],
        'key': cate['key'],
        'meta': cate['meta'],
    }
