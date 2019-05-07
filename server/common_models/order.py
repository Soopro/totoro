# coding=utf-8
from __future__ import absolute_import

from document import BaseDocument, ObjectId, INDEX_DESC
from utils.misc import now, parse_int, numid


class Order(BaseDocument):
    encrypt_secret_field = 'user_id'

    (STATUS_PENDING,
     STATUS_PAID,
     STATUS_SHIPPED,
     STATUS_DONE,
     STATUS_REFUNDED) = (0, 1, 2, 3, 4)

    METHOD_WXPAY = u'WXPAY'
    METHOD_ALIPAY = u'ALIPAY'

    MAX_QUERY = 60
    MAX_ITEMS = 60

    TIME_BETWEEN = 3600 * 24 * 31  # between 1 months.

    structure = {
        'user_id': ObjectId,
        'member_id': ObjectId,
        'customer_id': unicode,
        'merchant_id': unicode,
        'method': unicode,
        'trade_id': unicode,
        'transaction_id': unicode,
        'refund_id': unicode,
        'delivery': unicode,
        'items': [{
            'id': unicode,
            'item_id': unicode,
            'name': unicode,
            'detail': unicode,
            'price': int,
            'amount': int,
            'discounts': [unicode],
        }],
        'name': unicode,
        'recipient': unicode,
        'payment': int,
        'discount': int,
        'courier_fee': int,
        'credit_reward': int,
        'credit_payment': int,
        'voucher_payment': int,
        'bargain_payment': int,
        'redeem_payment': int,
        'redeem_code': unicode,
        'note': unicode,
        'bill_create_ip': unicode,
        'memo': unicode,
        'status': int,
        'creation': int,
        'updated': int,
    }
    required_fields = ['user_id', 'customer_id', 'merchant_id', 'method']
    default_values = {
        'member_id': None,
        'trade_id': numid,
        'transaction_id': u'',
        'refund_id': u'',
        'delivery': u'',
        'items': [],
        'name': u'',
        'recipient': u'',
        'payment': 0,
        'discount': 0,
        'credit_reward': 0,
        'credit_payment': 0,
        'voucher_payment': 0,
        'bargain_payment': 0,
        'redeem_payment': 0,
        'redeem_code': u'',
        'courier_fee': 0,
        'note': u'',
        'bill_create_ip': u'',
        'memo': u'',
        'status': STATUS_PENDING,
        'creation': now,
        'updated': now,
    }
    indexes = [
        {
            'fields': ['user_id'],
        },
        {
            'fields': ['user_id', 'customer_id'],
        },
        {
            'fields': ['user_id', 'customer_id', 'status'],
        },
        {
            'fields': ['user_id', 'merchant_id'],
        },
        {
            'fields': ['user_id', 'merchant_id', 'trade_id'],
            'unique': True,
        },
        {
            'fields': ['user_id', 'creation'],
        },
        {
            'fields': ['user_id', 'status'],
        },
        {
            'fields': ['creation'],
        },
        {
            'fields': ['updated'],
        }
    ]

    def find_one_by_id(self, _id):
        return self.find_one({
            '_id': ObjectId(_id),
        })

    def find_one_by_uid_id(self, user_id, _id):
        return self.find_one({
            'user_id': ObjectId(user_id),
            '_id': ObjectId(_id),
        })

    def find_one_by_uid_mchid_tid(self, user_id, merchant_id, trade_id):
        return self.find_one({
            'user_id': ObjectId(user_id),
            'merchant_id': merchant_id,
            'trade_id': trade_id,
        })

    def find_one_by_uid_mchid_cusid_id(self, user_id, merchant_id,
                                       customer_id, order_id, status=None):
        _query = {
            '_id': ObjectId(order_id),
            'user_id': ObjectId(user_id),
            'customer_id': customer_id,
            'merchant_id': merchant_id,
        }
        if status is not None:
            _query.update({
                'status': parse_int(status)
            })
        return self.find_one(_query)

    def find_by_uid_mchid(self, user_id, merchant_id, status=None):
        _query = {
            'user_id': ObjectId(user_id),
            'merchant_id': merchant_id
        }
        if status is not None:
            _query.update({
                'status': parse_int(status)
            })
        _sorts = [('updated', INDEX_DESC)]
        return self.find(_query).sort(_sorts).limit(self.MAX_QUERY)

    def find_by_uid(self, user_id, status=None):
        _query = {
            'user_id': ObjectId(user_id)
        }
        if status is not None:
            _query.update({
                'status': parse_int(status)
            })
        _sorts = [('updated', INDEX_DESC)]
        return self.find(_query).sort(_sorts).limit(self.MAX_QUERY)

    def find_by_uid_custid(self, user_id, customer_id, timestamp=None):
        _query = {
            'user_id': ObjectId(user_id),
            'customer_id': customer_id,
            'status': {'$ne': self.STATUS_PENDING},
        }
        _sorts = [('creation', INDEX_DESC)]
        if timestamp:
            _query.update({
                'updated': {'$lt': parse_int(timestamp)}
            })
        return self.find(_query).sort(_sorts).limit(self.MAX_QUERY)

    def search_by_uid(self, user_id, status=None,
                      trade_id=None, transaction_id=None,
                      start_time=None, end_time=None):
        start_time = parse_int(start_time)
        end_time = parse_int(end_time)

        if not end_time:
            end_time = now()
        if not start_time:
            start_time = end_time - self.TIME_BETWEEN

        _query = {
            'user_id': ObjectId(user_id),
            'creation': {
                '$gt': start_time,
                '$lt': end_time
            }
        }
        if trade_id:
            _query.update({
                'trade_id': trade_id
            })
        if transaction_id:
            _query.update({
                'transaction_id': transaction_id
            })
        if status is not None:
            _query.update({
                'status': parse_int(status)
            })
        _sorts = [('updated', INDEX_DESC)]
        return self.find(_query).sort(_sorts).limit(self.MAX_QUERY)

    def count_used(self, user_id):
        return self.find({
            'user_id': ObjectId(user_id)
        }).count()

    def clear_pending_by_uid(self, user_id):
        return self.collection.remove({
            'user_id': ObjectId(user_id),
            'status': self.STATUS_PENDING,
            'updated': {
                '$lt': now() - 3600 * 48,
            }
        })
