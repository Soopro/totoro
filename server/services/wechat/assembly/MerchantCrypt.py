# coding=utf-8
from __future__ import absolute_import

from Crypto.Cipher import AES
import base64
import hashlib


class MerchantCrypt(object):

    aes_key = None
    mode = AES.MODE_ECB

    def __init__(self, mch_key):
        if not isinstance(mch_key, basestring):
            raise Exception('[error]: mch_key invalid !')
        md5_hash = hashlib.md5()
        md5_hash.update(mch_key)
        self.aes_key = md5_hash.hexdigest()

    def _unpad(self, decrypted):
        pad = ord(decrypted[-1])
        return decrypted[:-pad]

    def decrypt(self, text):
        try:
            cryptor = AES.new(self.aes_key, self.mode)
            decrypted = cryptor.decrypt(base64.b64decode(text))
            return self._unpad(decrypted)
        except Exception:
            raise Exception('[error]: mch decrypt failed !')
