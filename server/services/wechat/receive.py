# coding=utf-8
from __future__ import absolute_import

import hashlib
import time
import HTMLParser

from .assembly.crypt import WeChatCrypt
from .core import WeChatBase, WeChatError


class WeChatReceiverAPI(WeChatBase):
    app_id = None
    token = None
    encodingAESKey = None
    crypter = None

    def __init__(self, token, app_id=None, aes_key=None):
        self.token = token
        self.app_id = app_id
        self.encodingAESKey = aes_key
        if token and app_id and aes_key:
            self.crypter = WeChatCrypt(token, aes_key, app_id)

    def validate(self, args_obj):
        signature = args_obj.get('signature', '')
        timestamp = args_obj.get('timestamp', '')
        nonce = args_obj.get('nonce', '')
        return signature == self._make_signature(timestamp, nonce)

    def _make_signature(self, timestamp, nonce):
        ln = [self.token, timestamp, nonce]
        ln = sorted(ln)
        base = ''.join(ln)
        signed = hashlib.sha1(base)
        return signed.hexdigest()

    def receive(self, receive_data, args_obj):
        if args_obj.get('encrypt_type') == 'aes':
            if not self.crypter:
                raise WeChatError.ReceiveError('no crypter.')
            receive_data = self.crypter.decrypt_msg(receive_data,
                                                    args_obj['msg_signature'],
                                                    args_obj['timestamp'],
                                                    args_obj['nonce'])
        data = self._parse_xml(receive_data)
        data['encrypt_type'] = args_obj.get('encrypt_type')
        data['nonce'] = args_obj.get('nonce')
        return data

    def response(self, receive_data, resp):
        to_user = receive_data.get('from_user_name')
        from_user = receive_data.get('to_user_name')
        if resp['msg_type'] == 'text':
            reply = TextReplyTmpl(to_user, from_user, resp.get('text', u''))
        elif resp['msg_type'] == 'news':
            reply = NewsReplyTmpl(to_user, from_user, resp.get('items', []))
        else:
            # TODO: support other response types.
            pass

        result = reply.render()
        if receive_data.get('encrypt_type') == 'aes':
            if not self.crypter:
                raise WeChatError.ResponseError('no crypter.')
            result = self.crypter.encrypt_msg(result.encode('utf-8'),
                                              receive_data.get('nonce'))
        return result


"""
response templates
"""


class ReplyTmpl(object):
    def __init__(self, to_user, from_user):
        self.to_user = to_user
        self.from_user = from_user


class TextReplyTmpl(ReplyTmpl):
    tmpl = u'''
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%d</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    </xml>
    '''

    def __init__(self, to_user, from_user, content):
        super(TextReplyTmpl, self).__init__(to_user, from_user)
        self.content = content or u''

    def render(self):
        return self.tmpl % (self.to_user,
                            self.from_user,
                            int(time.time()),
                            self.content)


class NewsReplyTmpl(ReplyTmpl):

    MAX_ITEMS = 1  # fucked by wechat api, they turned max 8 to 1.

    tmpl = u'''
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%d</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>%d</ArticleCount>
    <Articles>%s</Articles>
    </xml>
    '''

    tmpl_item = u'''
    <item>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <PicUrl><![CDATA[%s]]></PicUrl>
    <Url><![CDATA[%s]]></Url>
    </item>'''

    def __init__(self, to_user, from_user, items):
        super(NewsReplyTmpl, self).__init__(to_user, from_user)
        if not isinstance(items, list):
            items = []
        self.items = [{
            'title': item.get('title') or u'',
            'content': item.get('content') or u'',
            'picurl': item.get('picurl') or u'',
            'url': item.get('url') or u'',
        } for item in items][:self.MAX_ITEMS]

    def render_item(self):
        html_parser = HTMLParser.HTMLParser()
        unescape = html_parser.unescape
        item_str_list = [self.tmpl_item % (
                         unescape(item['title']),
                         unescape(item['content']),
                         item['picurl'],
                         item['url']) for item in self.items]
        return u''.join(item_str_list)

    def render(self):
        return self.tmpl % (self.to_user,
                            self.from_user,
                            int(time.time()),
                            len(self.items),
                            self.render_item())
