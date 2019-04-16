# coding=utf-8
from __future__ import absolute_import

from ..core import WeChatAccess


class WeChatCommWifiAPI(WeChatAccess):

    def get_qrcode(self, shop_id, ssid=None, img_id=0):
        """ img_id
        0 - original qr code
        1 - 155mm×215mm (w x h) qr code poster
        """
        path = '/bizwifi/qrcode/get'
        data = {
            'shop_id': shop_id,
            'img_id': img_id
        }
        if ssid:
            data.update(ssid=ssid)
        return self._request('POST', path, data=data)

    def get_statistics(self, begin_date, end_date, shop_id=-1):
        """ shop_id
        -1 - for total
        """
        path = '/bizwifi/statistics/list'
        data = {
            'begin_date': begin_date,
            'end_date': end_date,
            'shop_id': shop_id
        }
        return self._request('POST', path, data=data)

    def list_devices(self, shop_id=None, pageindex=1, pagesize=12):
        path = '/bizwifi/device/list'
        data = {
            'pageindex': pageindex,
            'pagesize': pagesize
        }
        if shop_id:
            data.update(shop_id=shop_id)

        devices = []
        result = self._request('POST', path, data=data)

        for record in result['data']['records']:
            if record.get('protocol_type') != 4:
                continue
            qr_url = self.get_qrcode(record['shop_id'], record['ssid'])
            qr_brand_url = self.get_qrcode(record['shop_id'],
                                           record['ssid'],
                                           img_id=1)
            devices.append({
                'qr_url': qr_url,
                'qr_brand_url': qr_brand_url,
                'shop_id': record['shop_id'],
                'ssid': record['ssid'],
                'bssid': record['bssid'],
                'pwd': record.get('password', u''),
                'protocol_type': record['protocol_type']
            })

        return {
            'devices': devices,
            'totalcount': result['data']['totalcount'],
            'pageindex': result['data']['pageindex']
        }

    def add_device(self, shop_id, ssid, password):
        path = '/bizwifi/device/add'
        data = {
            'shop_id': shop_id,
            'ssid': ssid,
            'password': password
        }
        self._request('POST', path, data=data)
        qr_url = self.get_qrcode(shop_id, ssid)
        qr_brand_url = self.get_qrcode(shop_id, ssid, img_id=1)

        return {
            'qr_url': qr_url,
            'qr_brand_url': qr_brand_url,
            'shop_id': shop_id,
            'ssid': ssid,
            'bssid': u'',
            'pwd': password,
            'protocol_type': 4,
        }

    def del_device(self, bssid):
        path = '/bizwifi/device/delete'
        data = {
            'bssid': bssid
        }
        return self._request('POST', path, data=data)

    def list_by_shop(self, pageindex=1, pagesize=20):
        path = '/bizwifi/shop/list'
        data = {
            'pageindex': pageindex,
            'pagesize': pagesize
        }

        result = self._request('POST', path, data=data)

        shop_list = []
        for record in result['data']['records']:
            shop_list.append({
                'shop_name': record.get('shop_name'),
                'shop_id': record.get('shop_id'),
                'ssid': record.get('ssid'),
                'ssid_list': record.get('ssid_list', []),
                'protocol_type': record.get('protocol_type')
            })

        return {
            'shops': shop_list,
            'totalcount': result['data']['totalcount'],
            'pageindex': result['data']['pageindex']
        }

    def get_by_shop(self, shop_id):
        path = '/bizwifi/shop/get'
        data = {
            'shop_id': shop_id
        }
        shop = self._request('POST', path, data=data)
        return shop['data']

    def update_by_shop(self, shop_id, old_ssid, ssid, password):
        path = '/bizwifi/shop/update'
        data = {
            'shop_id': shop_id,
            'old_ssid': old_ssid,
            'password': password,
        }
        if ssid != old_ssid:
            data.update({
                'ssid': ssid,
            })

        self.do_request('POST', path, data=data)
        qr_url = self.get_qrcode(shop_id, ssid)
        qr_brand_url = self.get_qrcode(shop_id, ssid, img_id=1)

        return {
            'ssid': ssid,
            'pwd': password,
            'qr_url': qr_url,
            'qr_brand_url': qr_brand_url,
        }

    def clear_by_shop(self, shop_id, ssid=None):
        path = '/bizwifi/shop/clean'
        data = {
            'shop_id': shop_id
        }
        if ssid:
            data.update(ssid=ssid)
        return self._request('POST', path, data=data)

    def set_homepage(self, shop_id, url=None):
        '''template_id
        0 - default template
        1 - custom url
        '''
        '''struct
        leave it empty if template_id is 0.
        '''
        '''url
        required if template_id is 1.
        '''
        path = '/bizwifi/homepage/set'
        if url:
            data = {
                'shop_id': shop_id,
                'template_id': 1,
                'struct': {
                    'url': url
                }
            }
        else:
            data = {
                'shop_id': shop_id,
                'template_id': 0
            }
        return self._request('POST', path, data=data)

    def get_homepage(self, shop_id, img_id):
        path = '/bizwifi/homepage/get'
        data = {
            'shop_id': shop_id
        }
        return self._request('POST', path, data=data)

    def set_finishpage(self, shop_id, url=None):
        path = '/bizwifi/finishpage/set'
        data = {
            'shop_id': shop_id,
            'finishpage_url': url or ''
        }
        return self._request('POST', path, data=data)

    def set_bartype(self, shop_id, bar_type):
        '''bar_type
        0-- Welcome + account name.
        1-- Welcome + shop name.
        2-- Connected + account name + Wi-Fi.
        3-- Connected + shop name + Wi-Fi.
        '''
        path = '/bizwifi/bar/set'
        data = {
            'shop_id': shop_id,
            'bar_type': bar_type
        }
        return self._request('POST', path, data=data)
