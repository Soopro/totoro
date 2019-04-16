# coding=utf-8
from __future__ import absolute_import

import re

from ..core import WeChatAccess
from ..assembly.WXBizDataCrypt import WXBizDataCrypt


class WeChatMinaAPI(WeChatAccess):

    def _decrypt(self, session_key, encrypted_data, iv):
        decrypter = WXBizDataCrypt(self.app_id, session_key)
        return decrypter.decrypt(encrypted_data, iv)

    def get_session(self, code):
        path_pairs = [
            '/sns/jscode2session',
            '?appid={appid}',
            '&secret={secret}',
            '&js_code={code}',
            '&grant_type=authorization_code'
        ]
        path = u''.join(path_pairs).format(appid=self.app_id,
                                           secret=self.app_secret,
                                           code=code)
        data = self._request('GET', path, access=False)
        return {
            'openid': data['openid'],
            'session_key': data['session_key'],
            'unionid': data.get('unionid')
        }

    def get_bound_phone(self, session_key, encrypted_data, iv):
        result = self._decrypt(session_key, encrypted_data, iv)
        return {
            'phone_number': result['phoneNumber'],
            'pure_phone_number': result['purePhoneNumber'],
            'country_code': result['countryCode'],
            'phonenum': u'{}-{}'.format(result['countryCode'],
                                        result['purePhoneNumber'])
        }

    # scan codes
    def create_qrcode(self, page_path=u'', width=480, with_dataurl=False):
        path = '/cgi-bin/wxaapp/createwxaqrcode'
        page_path = page_path.strip('/')

        data = {
            'path': page_path[:128] or u'pages/index/index',
            'width': int(width),
        }
        res = self._request('POST', path, data=data)
        return self._wrap_minacode(res, with_dataurl)

    def get_minacode(self, page_path=u'', width=480,
                     auto_color=True, line_color={},
                     is_hyaline=False, with_dataurl=False):
        path = '/wxa/getwxacode'
        page_path = page_path.strip('/')

        if not isinstance(line_color, dict):
            line_color = {}

        data = {
            'path': page_path[:128] or u'pages/index/index',
            'width': int(width),
            'is_hyaline': bool(is_hyaline),
            'auto_color': bool(auto_color),
            'line_color': {
                'r': line_color.get('r', 0),
                'g': line_color.get('g', 0),
                'b': line_color.get('b', 0)
            },
        }
        res = self._request('POST', path, data=data)
        return self._wrap_minacode(res, with_dataurl)

    def get_minacode_unlimit(self, scene=u'', page_path=u'', width=480,
                             auto_color=True, line_color={},
                             is_hyaline=False, with_dataurl=False):
        path = '/wxa/getwxacodeunlimit'
        regex = r'[^0-9a-zA-Z\!\#\$\&\'\(\)\*\+\,\/\:\;\=\?\@\-\.\_\~]'
        scene = re.sub(regex, u'', scene)[:32] or 'none'
        page_path = page_path.strip('/').split('?')[0].split('#')[0]

        if not isinstance(line_color, dict):
            line_color = {}

        data = {
            'scene': scene,
            'page': page_path[:128],
            'width': int(width),
            'is_hyaline': bool(is_hyaline),
            'auto_color': bool(auto_color),
            'line_color': {
                'r': line_color.get('r', 0),
                'g': line_color.get('g', 0),
                'b': line_color.get('b', 0)
            },
        }
        res = self._request('POST', path, data=data)
        return self._wrap_minacode(res, with_dataurl)

    def _wrap_minacode(self, res, with_dataurl=False):
        if with_dataurl:
            dataurl = self._gen_dataurl(res['mimetype'], res['stream'])
        else:
            dataurl = u''
        filename = self._gen_filename(u'minicode-{}'.format(self.app_id),
                                      res['mimetype'])
        return {
            'filename': filename,
            'content_type': res['content_type'],
            'mimetype': res['mimetype'],
            'stream': res['stream'],
            'dataurl': dataurl,
        }
