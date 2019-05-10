# coding=utf-8
from __future__ import absolute_import

import time
import base64
import hashlib
import envs

from Crypto import Random
from Crypto.Cipher import AES

from inflection import underscore, pluralize
from mongokit import (Document, OR, ObjectId, Connection, Cursor,
                      DocumentMigration,
                      INDEX_DESCENDING, INDEX_ASCENDING)
from mongokit.document import DocumentProperties


# aliases
MongodbConn = Connection
ObjectId = ObjectId
INDEX_DESC = INDEX_DESCENDING
INDEX_ASC = INDEX_ASCENDING
Cursor = Cursor
DocumentMigration = DocumentMigration
OR = OR


class MetaDoc(DocumentProperties):

    def __init__(cls, name, bases, attrs):
        super(MetaDoc, cls).__init__(name, bases, attrs)
        if not name.startswith('Callable'):
            if '__collection__' not in cls.__dict__:
                cls.__collection__ = pluralize(underscore(cls.__name__))
        return


# models
class BaseDocument(Document):
    __metaclass__ = MetaDoc
    use_schemaless = False

    secret_key_prefix = envs.DB_SECRET_PREFIX or '$b02NT~P=I$e*QZ'
    # migrate all encrypted data when change it.

    encrypt_secret_field = '_id'
    encrypt_mode = AES.MODE_ECB
    encrypt_block_size = AES.block_size

    sensitive_fields = []

    @staticmethod
    def _sensitive_filter(obj, repl='*'):
        if not dfa_filter.status:
            return obj
        elif isinstance(obj, basestring):
            return dfa_filter.filter(obj, repl)
        elif isinstance(obj, dict):
            res = {}
            for k, v in obj.iteritems():
                res[k] = dfa_filter.filter(v, repl)
            return res
        elif isinstance(obj, list):
            res = []
            for item in obj:
                res.append(dfa_filter.filter(item, repl))
            return res
        else:
            return obj

    def save(self, *args, **kwargs):
        for key in self.sensitive_fields:
            self[key] = self._sensitive_filter(self[key])
        if 'updated' in self:
            self['updated'] = int(time.time())
        return super(BaseDocument, self).save(*args, **kwargs)

    def write(self, *args, **kwargs):
        return super(BaseDocument, self).save(*args, **kwargs)

    # encryption (for unicode only)
    def encrypt(self, key, raw):
        if not raw:
            self[key] = raw
            return
        try:
            self[key] = self._encrypt(raw)
        except Exception as e:
            raise Exception('Document encrypt failed: {}'.format(str(e)))
        return self[key]

    def decrypt(self, key, key_prefix=None):
        if not self[key]:
            return self[key]
        try:
            return self._decrypt(self[key], key_prefix)
        except Exception:
            return self[key]

    def _encrypt(self, raw):
        if isinstance(raw, unicode):
            raw = raw.encode('utf-8')
        aes_key = self._get_aes_key()
        raw = self._pad(raw)
        iv = Random.new().read(self.encrypt_block_size)
        cipher = AES.new(aes_key, self.encrypt_mode, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')

    def _decrypt(self, enc, key_prefix=None):
        enc = base64.b64decode(enc)
        iv = enc[:self.encrypt_block_size]
        aes_key = self._get_aes_key(key_prefix)
        cipher = AES.new(aes_key, self.encrypt_mode, iv)
        return self._unpad(
            cipher.decrypt(enc[self.encrypt_block_size:])
        ).decode('utf-8')

    def _get_aes_key(self, key_prefix=None):
        key = self[self.encrypt_secret_field]
        _prefix = key_prefix or self.secret_key_prefix
        secret_key = u'{}.{}'.format(_prefix or u'', key)
        return hashlib.md5(secret_key).hexdigest()

    def _pad(self, s):
        _bs = self.encrypt_block_size
        return s + (_bs - len(s) % _bs) * chr(_bs - len(s) % _bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]


# filters
class DFAFilter():

    """Filter Messages from keywords
    Use DFA to keep algorithm perform constantly
    >>> f = DFAFilter()
    >>> f.add('fuck')
    >>> f.filter('hello fuck buddy')
    hello **** buddy
    """

    def __init__(self, path=None):
        self.keyword_chains = {}
        self.delimit = '\x00'
        if path:
            self.parse(path, True)

    @property
    def status(self):
        return bool(self.keyword_chains)

    def parse(self, path, required=True):
        try:
            with open(path) as f:
                for line in f:
                    self.add(line.strip())
        except Exception as e:
            if required:
                msg = 'DFAFilter: Dictionary text parse failed. '
                raise Exception(msg + str(e))

    def add(self, keyword):
        if not isinstance(keyword, unicode):
            keyword = keyword.decode('utf-8')
        chars = keyword.lower().strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in xrange(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in xrange(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def in_latin_word(self, message, start, step_ins):
        start_char = message[start]
        if 0x4e00 <= ord(start_char) < 0x9fa6:  # is chinese
            return False
        if start > 0 and \
           (ord(message[start - 1]) < 0x4e00 or
            ord(message[start - 1]) >= 0x9fa6) and \
           message[start - 1].isalnum():
            return True
        if start + step_ins < len(message) and \
           (ord(message[start + step_ins]) < 0x4e00 or
            ord(message[start + step_ins]) >= 0x9fa6) and \
           message[start + step_ins].isalnum():
            return True
        return False

    def filter(self, message, repl="*"):
        if not isinstance(message, str) and not isinstance(message, unicode):
            return message

        if isinstance(message, str):
            message = message.decode('utf-8')
        content_list = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        if self.in_latin_word(message, start, step_ins):
                            step_end = start + step_ins
                            content_list.append(message[start:step_end])
                            start += step_ins - 1
                            break
                        else:
                            content_list.append(repl * step_ins)
                            start += step_ins - 1
                            break
                else:
                    content_list.append(message[start])
                    break
            else:
                content_list.append(message[start])
            start += 1
        result = ''.join(content_list)
        return unicode(result)

    def check_legal(self, message, user_id):
        if not isinstance(message, unicode):
            message = message.decode('utf-8')
        message = message.lower()
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        return False
            start += 1
        return True


dfa_filter = DFAFilter('badwords.txt')
