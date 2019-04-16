# coding=utf-8
from __future__ import absolute_import

from itsdangerous import JSONWebSignatureSerializer
import requests
import json
import string
import random
import hashlib
import base64
import mimetypes
from inflection import underscore
import xml.etree.cElementTree as ET

from . import errors as WeChatError

STRING_ALL = string.ascii_uppercase + string.ascii_lowercase + string.digits


class WeChatBase(object):

    def _nonce(self, dig=20):
        r = random.SystemRandom()
        return ''.join([r.choice(STRING_ALL) for _ in xrange(dig)])

    def _md5(self, text):
        if isinstance(text, list):
            text = u''.join(t for t in text if isinstance(t, basestring))
        return hashlib.md5(text).hexdigest()

    def _b64encode(self, text):
        return base64.b64encode(text)

    def _b64decode(self, text):
        return base64.b64decode(text)

    def _parse_xml(self, xml_body):
        tree = ET.fromstring(xml_body)
        result = dict()
        for child in tree.getchildren():
            tag = underscore(child.tag)
            if not child.text:
                text = u''
            elif not isinstance(child.text, unicode):
                text = unicode(child.text)
            else:
                text = child.text
            result[tag] = text
        return result


class WeChatAccess(WeChatBase):
    WX_API_BASE_URL = 'https://api.weixin.qq.com'

    PREFIX_ACCESS = 'WECHAT_API:ACCESS_TOKEN/'

    PROGRESS_LOCK = 'HOLD'

    HEADERS = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    ACCESS_ERRCODES = (40001, 40014, 42001, 42007)
    OVERRUN_ERRCODE = (45009,)
    UNAUTH_ERRCODE = (48001, 48003)
    WHITELIST_ERRCODE = (40164,)
    BUSY_ERRCODE = (-1,)

    app_id = None
    app_secret = None

    redis_read = None
    redis_write = None
    auto_retry = True

    @property
    def key_access_token(self):
        return '{}{}'.format(self.PREFIX_ACCESS, self.app_id)

    @property
    def s(self):
        return JSONWebSignatureSerializer(secret_key=self.app_secret,
                                          salt=self.app_id)

    def __init__(self, app_id, app_secret, redis_read, redis_write=None,
                 auto_retry=True, clean_cached=False,
                 access_base_url=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redis_read = redis_read
        self.redis_write = redis_write or redis_read
        self.auto_retry = auto_retry

        if access_base_url:
            self.access_base_url = access_base_url
        else:
            self.access_base_url = self.WX_API_BASE_URL

        if clean_cached:
            self.__clean_cached()

    def __clean_cached(self):
        self.redis_write.delete(self.key_access_token)

    def __make_request(self, method, url, params, data,
                       files=None, timeout=None):
        res = requests.request(method,
                               url,
                               params=params,
                               data=data,
                               timeout=timeout,
                               files=files,
                               headers=None if files else self.HEADERS)
        res.encoding = 'utf-8'
        res.raise_for_status()
        res_content_type = res.headers.get('Content-Type', u'')
        if res_content_type.startswith('image/'):
            mimetype = res_content_type.split(';')[0].strip()
            return {
                'content_type': res_content_type,
                'mimetype': mimetype,
                'stream': res.content,
            }
        else:
            return res.json()

    def __raise_for_error(self, result):
        if not result.get('errcode'):
            return result
        elif result.get('errcode') in self.WHITELIST_ERRCODE:
            raise WeChatError.APINotIPWhitelist(result)
        elif result.get('errcode') in self.BUSY_ERRCODE:
            raise WeChatError.APIBusy(result)
        elif result.get('errcode') in self.OVERRUN_ERRCODE:
            raise WeChatError.APIOverrun(result)
        elif result.get('errcode') in self.UNAUTH_ERRCODE:
            raise WeChatError.APIUnauthorized(result)
        elif result.get('errcode'):
            raise WeChatError.OPError(result)
        else:
            return result

    def _gen_filename(self, name, ext):
        if '/' in ext:
            ext = mimetypes.guess_extension(ext) or '.unknow'
        if ext in ['.jpe']:  # keep jpg is jpg or jpeg.
            ext = '.jpg'
        return u'{}{}'.format(name, ext)

    def _gen_dataurl(self, mimetype, stream):
        return u'data:{};base64,{}'.format(mimetype, base64.b64encode(stream))

    def _request(self, method, path, params=None, data=None, files=None,
                 timeout=10, access=True):
        if path.startswith('https://'):
            url = path
        else:
            url = '{}/{}'.format(self.WX_API_BASE_URL, path.strip('/'))

        if access:
            token = self._access_token()
            if not isinstance(params, dict):
                params = {}
            params['access_token'] = token['access_token']

        if data is not None:
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')

        result = self.__make_request(method=method,
                                     url=url,
                                     params=params,
                                     data=data,
                                     files=files,
                                     timeout=timeout)

        if result.get('errcode') in self.ACCESS_ERRCODES and self.auto_retry:
            if access:
                token = self._refresh_token()
                params['access_token'] = token['access_token']
            result = self.__make_request(method=method,
                                         url=url,
                                         params=params,
                                         data=data,
                                         files=files,
                                         timeout=timeout)
        self.__raise_for_error(result)
        return result

    def _access_token(self):
        access_token = self.redis_read.get(self.key_access_token)
        if access_token == self.PROGRESS_LOCK:
            raise WeChatError.APIBusy('too many access_token')
        elif access_token:
            expires_in = self.redis_read.ttl(self.key_access_token)
            return {
                'access_token': self.s.loads(access_token),
                'expires_in': expires_in
            }

        # temporary locked progress
        self.redis_write.setex(self.key_access_token, self.PROGRESS_LOCK, 60)

        api_url = '{}/cgi-bin/token'.format(self.access_base_url)
        params = {
            'appid': self.app_id,
            'secret': self.app_secret,
            'grant_type': 'client_credential',
        }
        resp = requests.get(api_url,
                            params=params,
                            timeout=6,
                            headers=self.HEADERS)
        resp.encoding = 'utf-8'
        resp.raise_for_status()
        result = resp.json()

        if result.get('errcode'):
            self.redis_write.delete(self.key_access_token)
            self.__raise_for_error(result)

        self.redis_write.setex(self.key_access_token,
                               self.s.dumps(result['access_token']),
                               result['expires_in'] - 60)
        return {
            'access_token': result['access_token'],
            'expires_in': result['expires_in'],
        }

    def _refresh_token(self):
        access_token = self.redis_read.get(self.key_access_token)
        if access_token and access_token != self.PROGRESS_LOCK:
            self.redis_write.delete(self.key_access_token)
        return self._access_token()

    def get_access_token(self):
        return self._access_token()
