# coding=utf-8
from __future__ import absolute_import

from flask import current_app, g

from utils.response import output_json


@output_json
def list_volumes():
    user = g.curr_user
    volumes = current_app.mongodb.BookVolume.find_lend_by_uid(user['_id'])
    return [output_volume(vol) for vol in volumes]


@output_json
def list_records():
    user = g.curr_user
    records = current_app.mongodb.BookRecord.find_by_uid(user['_id'])
    return [output_record(record) for record in records]


# outputs
def output_volume(vol):
    return {
        'id': vol['_id'],
        'code': vol['code'],
        'borrower': vol['borrower'],
        'meta': vol['meta'],
        'status': vol['status'],
        'creation': vol['creation'],
        'updated': vol['updated'],
    }


def output_record(record):
    return {
        'id': record['_id'],
        'volume': record['volume'],
        'borrower': record['borrower'],
        'meta': record['meta'],
        'status': record['status'],
        'creation': record['creation'],
        'updated': record['updated'],
    }