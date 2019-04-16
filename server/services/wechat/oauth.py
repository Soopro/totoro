# coding=utf-8
from __future__ import absolute_import

import requests
import urllib

from .core import WeChatBase, WeChatError


class WeChatOAuthAPI(WeChatBase):

    WX_OPEN_BASE_URL = 'https://open.weixin.qq.com'
    WX_API_BASE_URL = 'https://api.weixin.qq.com'

    WX_OAUTH_SCOPE_BASE = 'snsapi_base'
    WX_OAUTH_SCOPE_INFO = 'snsapi_userinfo'

    HEADERS = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    app_id = None
    app_secret = None

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    def _request(self, url, skip_errcode=False):
        res = requests.get(url, headers=self.HEADERS)
        res.encoding = 'utf-8'
        res.raise_for_status()
        result = res.json()
        if result.get('errcode') and not skip_errcode:
            raise WeChatError.OPError(result)
        return result

    # code
    def code(self, redirect_uri, userinfo=False, state=u''):
        """
        generate a weixin auth page url, and redirect to it
        scope: 'snsapi_base' for only openid, 'snsapi_userinfo' for user info

        code can be used only once,
        and will be expired in 5 mins if not be used.
        """
        if userinfo:
            scope = self.WX_OAUTH_SCOPE_INFO
        else:
            scope = self.WX_OAUTH_SCOPE_BASE

        url_pairs = [
            self.WX_OPEN_BASE_URL,
            '/connect/oauth2/authorize',
            '?appid={appid}',
            '&redirect_uri={redirect_uri}',
            '&response_type=code',
            '&scope={scope}',
            '&state={state}',
            '#wechat_redirect'
        ]
        redirect_uri = urllib.quote(redirect_uri)
        return u''.join(url_pairs).format(appid=self.app_id,
                                          redirect_uri=redirect_uri,
                                          scope=scope,
                                          state=state)

    # access token
    """
    this access_tokoen is not Official account access_token.
    """
    def access(self, code):
        url_pairs = [
            self.WX_API_BASE_URL,
            '/sns/oauth2/access_token',
            '?appid={appid}',
            '&secret={secret}',
            '&code={code}',
            '&grant_type=authorization_code'
        ]
        url = u''.join(url_pairs).format(appid=self.app_id,
                                         secret=self.app_secret,
                                         code=code)
        data = self._request(url)
        return {
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'expires_in': data['expires_in'],
            'openid': data['openid'],
            'scope': data['scope'],
            'userinfo': data['scope'] == self.WX_OAUTH_SCOPE_INFO,
        }

    # refresh token
    def refresh(self, refresh_token):
        """
        refresh token if necessary
        :return:
        """
        url_pairs = [
            self.WX_API_BASE_URL,
            '/sns/oauth2/refresh_token',
            '?appid={appid}',
            '&grant_type=refresh_token'
            '&refresh_token={refresh_token}'
        ]
        url = u''.join(url_pairs).format(appid=self.app_id,
                                         refresh_token=refresh_token)
        data = self._request(url)
        return {
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'expires_in': data['expires_in'],
            'openid': data['openid'],
            'scope': data['scope'],
            'userinfo': data['scope'] == self.WX_OAUTH_SCOPE_INFO,
        }

    def userinfo(self, openid, access_token, lang='zh_CN'):
        url_pairs = [
            self.WX_API_BASE_URL,
            '/sns/userinfo',
            '?access_token={access_token}',
            '&openid={openid}&lang={lang}'
        ]
        url = u''.join(url_pairs).format(access_token=access_token,
                                         openid=openid,
                                         lang=lang)
        data = self._request(url)
        return {
            'openid': data['openid'],
            'nickname': data['nickname'],
            'sex': data['sex'],
            'province': data['province'],
            'city': data['city'],
            'country': data['country'],
            'headimgurl': data['headimgurl'],
            'privilege': data['privilege'],
            'unionid': data.get('unionid')
        }

    def validate(self, openid, access_token):
        url_pairs = [
            self.WX_API_BASE_URL,
            '/sns/auth',
            '?access_token={access_token}'
            '&openid={openid}'
        ]
        url = u''.join(url_pairs).format(access_token=access_token,
                                         openid=openid)
        data = self._request(url, skip_errcode=True)
        return not data.get('errcode')
