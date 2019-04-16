# coding=utf-8
from __future__ import absolute_import

import uuid
import time
import hashlib

from ..core import WeChatAccess


class WeChatCommAPI(WeChatAccess):
    PREFIX_JSTICKET = 'WECHAT_API:JSTICKET/'

    @property
    def key_jsticket(self):
        return '{}{}'.format(self.PREFIX_JSTICKET, self.app_id)

    def __clean_cached(self):
        pip = self.redis_write.pipeline(transaction=False)
        pip.delete(self.key_access_token)
        pip.delete(self.key_jsticket)
        pip.execute()

    def _jsticket(self, refresh):
        ticket = self.redis_read.get(self.key_jsticket)
        if ticket and not refresh:
            expires_in = self.redis_read.ttl(self.key_jsticket)
            return {
                'ticket': self.s.loads(ticket),
                'expires_in': expires_in
            }

        path = '/cgi-bin/ticket/getticket'
        params = {
            'type': 'jsapi',
        }

        result = self._request('GET', path, params=params)

        self.redis_write.setex(self.key_jsticket,
                               self.s.dumps(result['ticket']),
                               result['expires_in'] - 60)
        return {
            'ticket': result['ticket'],
            'expires_in': result['expires_in'],
        }

    # jssdk
    def jssdk_signature(self, url, refresh=False):
        jsticket = self._jsticket(refresh)
        ret = {
            'nonceStr': uuid.uuid4().hex[:16],
            'jsapi_ticket': jsticket['ticket'],
            'timestamp': int(time.time()),
            'url': url
        }
        sign_str = '&'.join(['%s=%s' % (k.lower(), ret[k])
                             for k in sorted(ret)])
        return {
            'app_id': self.app_id,
            'signature': hashlib.sha1(sign_str).hexdigest(),
            'nonce_str': ret['nonceStr'],
            'timestamp': ret['timestamp'],
            'url': url,
            'expires_in': jsticket['expires_in'],
        }

    # menu
    def get_menu(self):
        path = '/cgi-bin/menu/get'
        return self._request('GET', path)

    def set_menu(self, buttons):
        path = '/cgi-bin/menu/create'
        data = {'button': buttons}
        return self._request('POST', path, data=data)

    def del_menu(self):
        path = '/cgi-bin/menu/delete'
        return self._request('GET', path)

    # customer service
    def customer_service_reply(self, response):
        path = '/cgi-bin/message/custom/send'
        return self._request('POST', path, data=response)

    # notify
    def send_notify(self, to_user, template_id, send_data,
                    url=None, miniprogram=None):
        path = '/cgi-bin/message/template/send'
        data = {
            'touser': to_user,
            'template_id': template_id,
            'url': url,
            'miniprogram': miniprogram,
            'data': send_data
        }
        return self._request('POST', path, data=data)

    # subscribe
    def subscribe_info(self, openid):
        path = '/cgi-bin/user/info'
        params = {
            'openid': openid,
        }
        data = self._request('GET', path, params=params)

        return {
            'subscribe': data.get('subscribe', 0),
            'openid': data.get('openid'),
            'nickname': data.get('nickname'),
            'sex': data.get('sex'),
            'language': data.get('language'),
            'city': data.get('city'),
            'province': data.get('province'),
            'headimgurl': data.get('headimgurl'),
            'subscribe_time': data.get('subscribe_time'),
            'unionid': data.get('unionid'),
            'remark': data.get('remark'),
            'groupid': data.get('groupid'),
            'tagid_list': data.get('tagid_list'),
        }

    def get_openids(self):
        path = '/cgi-bin/user/get'
        return self._request('POST', path)

    def get_subscriber(self, openid, lang='zh_CN'):
        path = '/cgi-bin/user/info'
        params = {
            'openid': openid,
            'lang': lang
        }
        return self._request('POST', path, params=params)

    def get_subscribers(self, usr_list):
        path = '/cgi-bin/user/info/batchget'
        data = {
            'user_list': usr_list
        }
        return self._request('POST', path, data=data)

    def update_subscriber(self, openid, to_groupid):
        path = '/cgi-bin/groups/members/update'
        data = {
            'openid': openid,
            'to_groupid': to_groupid
        }
        return self._request('POST', path, data=data)

    def update_subscribers(self, openid_list, to_groupid):
        path = '/cgi-bin/groups/members/batchupdate'
        data = {
            'openid_list': openid_list,
            'to_groupid': to_groupid
        }
        return self._request('POST', path, data=data)

    # material
    def list_materials(self, count, offset, media_type='image'):
        count = 20
        offset = 0
        materials = []

        path = '/cgi-bin/material/batchget_material'

        data = {
            'type': media_type,
            'offset': offset,
            'count': count,
        }
        data = self._request('POST', path, data=data)
        materials = [item for item in data['item'] if 'url' in item]

        return {
            'total_count': data['total_count'],
            'item_count': data['item_count'],
            'materials': materials
        }

    def add_material(self, material_file, media_type='image'):
        path = '/cgi-bin/material/add_material'
        params = {
            'type': media_type,
        }
        files = {'media': material_file}
        return self._request('POST', path, params=params, files=files)

    def get_material(self, media_id):
        path = '/cgi-bin/material/get_material'
        data = {
            'media_id': media_id
        }
        return self._request('POST', path, data=data)

    def del_material(self, media_id):
        path = '/cgi-bin/material/del_material'
        data = {
            'media_id': media_id
        }
        return self._request('POST', path, data=data)

    def add_temp_material(self, tmp_material_file, media_type='image'):
        path = 'cgi-bin/media/upload'
        params = {
            'type': media_type,
        }
        files = {'media': tmp_material_file}
        return self._request('POST', path, params=params, files=files)

    def upload_img(self, img_file):
        path = 'cgi-bin/media/uploadimg'
        files = {'media': img_file}
        return self._request('POST', path, files=files)

    # broadcast
    def upload_news(self, articles):
        path = '/cgi-bin/media/uploadnews'
        data = {
            'articles': articles
        }
        return self._request('POST', path, data=data)

    def _process_send(self, send_data, preview_by):
        if preview_by:
            path = '/cgi-bin/message/mass/preview'
            send_data.update({
                'towxname': preview_by,
            })
        else:
            path = '/cgi-bin/message/mass/sendall'
            send_data.update({
                'filter': {
                    'is_to_all': True
                },
            })
        return path, send_data

    def send_text(self, text, preview_by=None):
        data = {
            'text': {
                'content': text
            },
            'msgtype': 'text',
        }
        path, data = self._process_send(data, preview_by)
        return self._request('POST', path, data=data)

    def send_news(self, news_media_id, preview_by=None):
        data = {
            'mpnews': {
                'media_id': news_media_id
            },
            'msgtype': 'mpnews',
            'send_ignore_reprint': 1,
        }
        path, data = self._process_send(data, preview_by)
        return self._request('POST', path, data=data)

    def send_image(self, image_media_id, preview_by=None):
        data = {
            'image': {
                'media_id': image_media_id
            },
            'msgtype': 'image',
        }
        path, data = self._process_send(data, preview_by)
        return self._request('POST', path, data=data)

    def del_sent(self, msg_id):
        path = '/cgi-bin/message/mass/delete'
        data = {
            'msg_id': msg_id
        }
        return self._request('POST', path, data=data)
