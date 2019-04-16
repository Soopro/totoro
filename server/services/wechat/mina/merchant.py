# coding=utf-8
from __future__ import absolute_import

import requests
import time
from datetime import datetime, timedelta

from ..assembly.MerchantCrypt import MerchantCrypt
from ..core import WeChatBase, WeChatError


class WeChatMinaMerchantAPI(WeChatBase):
    WX_MCH_BASE_URL = 'https://api.mch.weixin.qq.com'

    HEADERS = {
        'Content-Type': 'application/xml',
        'Accept': 'application/xml',
    }

    RESP_STATUS_SUCCESS = 'SUCCESS'
    RESP_STATUS_FAIL = 'FAIL'

    TRADE_TYPE = u'JSAPI'
    SIGN_TYPE = u'MD5'
    ORDER_EXPIRES_IN = 3600

    app_id = None
    mch_id = None
    mch_secret = None
    mch_name = u''
    mch_class = u''
    notify_url = u''

    # sign_type support `MD5` only.

    def __init__(self, app_id, mch_id, mch_secret,
                 mch_name=u'', mch_class=u'', notify_url=u''):
        self.app_id = app_id
        self.mch_id = mch_id
        self.mch_secret = mch_secret
        self.mch_name = mch_name
        self.mch_class = mch_class
        self.notify_url = notify_url

    def _get_expire_time(self, expires_in=None):
        if not expires_in:
            expires_in = self.ORDER_EXPIRES_IN
        elif len(str(int(expires_in))) == 13:
            expires_in = int(expires_in / 1000)
        try:
            expire_timestamp = int(time.time()) + expires_in
            date_object = datetime.fromtimestamp(expire_timestamp)
        except Exception:
            date_object = datetime.now() + timedelta(hours=1)
        return date_object.strftime('%Y%m%d%H%M%S')

    def _decrypt(self, text):
        decrypter = MerchantCrypt(self.mch_secret)
        result = decrypter.decrypt(text)
        return self._parse_xml(result)

    def _sign(self, payload):
        params = payload.copy()
        params.pop('sign', None)
        keys = params.keys()
        keys.sort()
        params_str = u'&'.join('%s=%s' % (key, params[key])
                               for key in keys if params[key])
        pm_str = u'{params_str}&key={secret}'.format(params_str=params_str,
                                                     secret=self.mch_secret)
        if isinstance(pm_str, unicode):
            pm_str = pm_str.encode('utf-8')
        return self._md5(pm_str).upper()

    def _check_sign(self, payload):
        sign = payload.get('sign')
        if sign:
            return sign == self._sign(payload)
        return True

    def _request(self, method, path, params=None, data=None, timeout=10):
        if path.startswith('https://'):
            url = path
        else:
            url = '{}/{}'.format(self.WX_MCH_BASE_URL, path.strip('/'))

        resp = requests.request(method, url, params=params, data=data,
                                timeout=timeout, headers=self.HEADERS)
        resp.encoding = 'utf-8'
        resp.raise_for_status()
        result = self._parse_xml(resp.content)
        if result.get('return_code') == self.RESP_STATUS_FAIL:
            raise WeChatError.MerchantError(result.get('return_msg'))
        elif result.get('result_code') == self.RESP_STATUS_FAIL:
            error = {
                'errcode': result.get('err_code'),
                'errmsg': result.get('err_code_des'),
            }
            raise WeChatError.MerchantError(error)
        elif not self._check_sign(result):
            raise WeChatError.MerchantError('result sign')
        return result

    def _receive(self, notify_xml):
        result = self._parse_xml(notify_xml)
        if result.get('return_code') == self.RESP_STATUS_FAIL:
            raise WeChatError.MerchantError(result.get('return_msg'))
        elif result.get('result_code') == self.RESP_STATUS_FAIL:
            error = {
                'errcode': result.get('err_code'),
                'errmsg': result.get('err_code_des'),
            }
            raise WeChatError.MerchantError(error)
        elif not self._check_sign(result):
            raise WeChatError.MerchantError('receive sign')
        return result

    def make_order(self, params):
        path = '/pay/unifiedorder'
        order = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'body': u'{}-{}'.format(self.mch_name, self.mch_class),
            'notify_url': self.notify_url,
            'nonce_str': self._nonce(),
            'attach': params.get('attach', u''),
            'detail': params.get('detail', u''),
            'trade_type': self.TRADE_TYPE,
            'out_trade_no': params['out_trade_no'],
            'spbill_create_ip': params['spbill_create_ip'],
            'openid': params['openid'],
            'total_fee': params['total_fee'],
            'goods_tag': params.get('goods_tag', u''),
            'time_expire': self._get_expire_time(params.get('expires_in'))
        }
        order['sign'] = self._sign(order)
        xml = MiniMakeOrderTmpl(order).render()
        result = self._request('POST', path, data=xml)
        package = u'prepay_id={}'.format(result['prepay_id'])
        timestamp = unicode(int(time.time()))
        pay_sign = self._sign({
            'appId': result['appid'],
            'nonceStr': result['nonce_str'],
            'package': package,
            'signType': self.SIGN_TYPE,
            'timeStamp': timestamp
        })
        return {
            'appid': result['appid'],
            'mch_id': result['mch_id'],
            'nonce_str': result['nonce_str'],
            'trade_type': result['trade_type'],
            'prepay_id': result['prepay_id'],
            'package': package,
            'timestamp': timestamp,
            'sign_type': self.SIGN_TYPE,
            'pay_sign': pay_sign,
        }

    def query_order(self, params):
        path = '/pay/orderquery'
        order = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': self._nonce(),
        }
        if 'transaction_id' in params:
            order['transaction_id'] = params['transaction_id']
        elif 'out_trade_no' in params:
            order['out_trade_no'] = params['out_trade_no']
        order['sign'] = self._sign(order)
        xml = MiniQueryOrderTmpl(order).render()
        result = self._request('POST', path, data=xml)
        status_map = {'NOTPAY': 0, 'SUCCESS': 1, 'REFUND': 2, 'CLOSED': 3,
                      'REVOKED': 4, 'USERPAYING': 5, 'PAYERROR': -1}
        return {
            'appid': result['appid'],
            'mch_id': result['mch_id'],
            'nonce_str': result['nonce_str'],
            'sign': result['sign'],
            'openid': result['openid'],
            'trade_type': result['trade_type'],
            'trade_state': result['trade_state'],
            'bank_type': result['bank_type'],
            'total_fee': result['total_fee'],
            'cash_fee': result['cash_fee'],
            'settlement_total_fee': result.get('settlement_total_fee'),
            'is_subscribe': result.get('is_subscribe'),
            'transaction_id': result['transaction_id'],
            'out_trade_no': result['out_trade_no'],
            'attach': result.get('attach'),
            'time_end': result['time_end'],
            'status': status_map.get(result['trade_state']),
        }

    def close_order(self, params):
        path = '/pay/closeorder'
        order = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': self._nonce(),
            'out_trade_no': params['out_trade_no'],
        }
        order['sign'] = self._sign(order)
        xml = MiniCloseOrderTmpl(order).render()
        result = self._request('POST', path, data=xml)
        return {
            'appid': result['appid'],
            'mch_id': result['mch_id'],
            'nonce_str': result['nonce_str'],
            'sign': result['sign'],
        }

    def receive_order_notify(self, notify_xml):
        result = self._receive(notify_xml)
        return {
            'appid': result['appid'],
            'mch_id': result['mch_id'],
            'nonce_str': result['nonce_str'],
            'sign': result['sign'],
            'openid': result['openid'],
            'trade_type': result['trade_type'],
            'bank_type': result['bank_type'],
            'total_fee': result['total_fee'],
            'cash_fee': result['cash_fee'],
            'settlement_total_fee': result.get('settlement_total_fee'),
            'is_subscribe': result.get('is_subscribe'),
            'transaction_id': result['transaction_id'],
            'out_trade_no': result['out_trade_no'],
            'attach': result.get('attach'),
            'time_end': result['time_end'],
        }

    def receive_refund_notify(self, notify_xml):
        result = self._receive(notify_xml)
        req_info = self._decrypt(result['req_info'])
        status_map = {'CHANGE': 0, 'SUCCESS': 1, 'REFUNDCLOSE': 2}
        return {
            'appid': result['appid'],
            'mch_id': result['mch_id'],
            'nonce_str': result['nonce_str'],
            'transaction_id': req_info['transaction_id'],
            'refund_id': req_info['refund_id'],
            'out_trade_no': req_info['out_trade_no'],
            'total_fee': req_info['total_fee'],
            'settlement_total_fee': req_info.get('settlement_total_fee'),
            'refund_fee': req_info['refund_fee'],
            'settlement_refund': req_info['settlement_refund'],
            'refund_status': req_info['refund_status'],
            'refund_recv_accout': result['refund_recv_accout'],
            'refund_account': result['refund_account'],
            'refund_request_source': result['refund_request_source'],
            'status': status_map.get(req_info['refund_status'], 0)
        }

    def response(self, message=u'OK'):
        status = self.RESP_STATUS_SUCCESS
        try:
            message = unicode(message)
        except Exception:
            message = u'OK'

        xml_data = u'''
        <xml>
          <return_code><![CDATA[{status}]]></return_code>
          <return_msg><![CDATA[{message}]]></return_msg>
        </xml>
        '''.format(status=status, message=message)
        return xml_data

    def reject(self, message='Error'):
        status = self.RESP_STATUS_FAIL
        try:
            message = unicode(message)
        except Exception:
            message = u'Error'

        xml_data = u'''
        <xml>
          <return_code><![CDATA[{status}]]></return_code>
          <return_msg><![CDATA[{message}]]></return_msg>
        </xml>
        '''.format(status=status, message=message)
        return xml_data


class MiniOrderTmpl(object):
    tmpl = u''

    def __init__(self, data):
        self.data = data

    def _render_xml(self):
        return self.tmpl

    def render(self):
        try:
            xml = self._render_xml()
            return xml.encode('utf-8')
        except Exception as e:
            raise WeChatError.ParameterStructureError(e)


class MiniQueryOrderTmpl(MiniOrderTmpl):
    tmpl = u'''
    <xml>
    <appid>{appid}</appid>
    <mch_id>{mch_id}</mch_id>
    <nonce_str>{nonce_str}</nonce_str>
    <out_trade_no>{out_trade_no}</out_trade_no>
    <transaction_id>{transaction_id}</transaction_id>
    <sign>{sign}</sign>
    </xml>
    '''

    def __init__(self, data):
        self.data = data

    def _render_xml(self):
        format_obj = {
            'appid': self.data['appid'],
            'mch_id': self.data['mch_id'],
            'nonce_str': self.data['nonce_str'],
            'transaction_id': self.data['transaction_id'],
            'out_trade_no': self.data['out_trade_no'],
            'sign': self.data['sign']
        }
        return self.tmpl.format(**format_obj)


class MiniMakeOrderTmpl(MiniOrderTmpl):
    tmpl = u'''
    <xml>
    <appid>{appid}</appid>
    <attach>{attach}</attach>
    <body>{body}</body>
    <mch_id>{mch_id}</mch_id>
    <detail><![CDATA[{detail}]]></detail>
    <nonce_str>{nonce_str}</nonce_str>
    <notify_url>{notify_url}</notify_url>
    <openid>{openid}</openid>
    <out_trade_no>{out_trade_no}</out_trade_no>
    <spbill_create_ip>{spbill_create_ip}</spbill_create_ip>
    <total_fee>{total_fee}</total_fee>
    <trade_type>{trade_type}</trade_type>
    <goods_tag>{goods_tag}</goods_tag>
    <time_expire>{time_expire}</time_expire>
    <sign>{sign}</sign>
    </xml>
    '''

    def __init__(self, data):
        self.data = data

    def _render_xml(self):
        format_obj = {
            'appid': self.data['appid'],
            'body': self.data['body'],
            'mch_id': self.data['mch_id'],
            'detail': self.data['detail'],
            'attach': self.data['attach'],
            'nonce_str': self.data['nonce_str'],
            'notify_url': self.data['notify_url'],
            'openid': self.data['openid'],
            'out_trade_no': self.data['out_trade_no'],
            'spbill_create_ip': self.data['spbill_create_ip'],
            'total_fee': self.data['total_fee'],
            'trade_type': self.data['trade_type'],
            'goods_tag': self.data['goods_tag'],
            'time_expire': self.data['time_expire'],
            'sign': self.data['sign']
        }
        return self.tmpl.format(**format_obj)


class MiniCloseOrderTmpl(MiniOrderTmpl):
    tmpl = u'''
    <xml>
    <appid>{appid}</appid>
    <mch_id>{mch_id}</mch_id>
    <nonce_str>{nonce_str}</nonce_str>
    <out_trade_no>{out_trade_no}</out_trade_no>
    <sign>{sign}</sign>
    </xml>
    '''

    def __init__(self, data):
        self.data = data

    def _render_xml(self):
        format_obj = {
            'appid': self.data['appid'],
            'mch_id': self.data['mch_id'],
            'nonce_str': self.data['nonce_str'],
            'out_trade_no': self.data['out_trade_no'],
            'sign': self.data['sign']
        }
        return self.tmpl.format(**format_obj)
