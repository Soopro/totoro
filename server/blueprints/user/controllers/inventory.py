# coding=utf-8
from __future__ import absolute_import

from flask import current_app, g

from utils.response import output_json


# volumes
@output_json
def list_volumes():
    user = g.curr_user
    volumes = current_app.mongodb.\
        BookVolume.find_lend_by_uid(user['_id'])
    pending_vols = current_app.mongodb.\
        BookVolume.find_pending_by_uid(user['_id'])
    volumes = list(pending_vols) + list(volumes)
    return [output_volume(vol) for vol in volumes]


# records
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
        'renter': vol['renter'],
        'rental_time': vol['rental_time'],
        'meta': vol['meta'],
        'status': vol['status'],
        'creation': vol['creation'],
        'updated': vol['updated'],
    }


def output_record(record):
    return {
        'id': record['_id'],
        'volume': record['volume'],
        'meta': record['meta'],
        'status': record['status'],
        'creation': record['creation'],
        'updated': record['updated'],
    }
