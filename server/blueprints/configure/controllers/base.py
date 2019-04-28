# coding=utf-8
from __future__ import absolute_import

from flask import g

from utils.response import output_json


@output_json
def get_configure():
    return output_configure(g.configure)


# outputs
def output_configure(configure):
    return {
        'meta': configure['meta']
    }
