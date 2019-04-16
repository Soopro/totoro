# coding=utf-8
from __future__ import absolute_import

from .WXBizMsgCrypt import WXBizMsgCrypt


class WeChatCrypt(object):
    def __init__(self, token, aes_key, app_id):
        if isinstance(token, unicode):
            token = token.encode('utf-8')
        if isinstance(aes_key, unicode):
            aes_key = aes_key.encode('utf-8')
        if isinstance(app_id, unicode):
            app_id = app_id.encode('utf-8')
        self.crypt_instance = WXBizMsgCrypt(token, aes_key, app_id)

    def encrypt_msg(self, to_xml, nonce):
        ret, encrypt_xml = self.crypt_instance.EncryptMsg(to_xml, nonce)
        if ret == 0:
            return encrypt_xml
        else:
            return None

    def decrypt_msg(self, from_xml, msg_sign, timestamp, nonce):
        ret, decryp_xml = self.crypt_instance.DecryptMsg(from_xml, msg_sign,
                                                         timestamp, nonce)
        if ret == 0:
            return decryp_xml
        else:
            return None
