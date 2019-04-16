# coding=utf-8
from __future__ import absolute_import

from werkzeug.utils import secure_filename
from slugify import slugify
from datetime import datetime
from functools import cmp_to_key
from bson import ObjectId
import os
import re
import uuid
import time
import string
import random
import json
import hashlib
import hmac
import urllib
import urlparse
import mimetypes


def route_inject(app_or_blueprint, url_patterns):
    for pattern in url_patterns:
        options = pattern[3] if len(pattern) > 3 else {}
        app_or_blueprint.add_url_rule(pattern[0],
                                      view_func=pattern[1],
                                      methods=pattern[2].split(),
                                      **options)


def _slug_safety_filter(slug):
    if slug[:1] and slug[:1].isdigit():
        slug = u's-{}'.format(slug)
    return slug[:120]  # slug must be under 120 letter.


def process_slug(value, autofill=True):
    try:
        slug = unicode(slugify(value))
    except Exception:
        slug = u''
    if not slug and autofill:
        slug = unicode(uuid.uuid4().hex[:6])
    return _slug_safety_filter(slug)


def slug_uuid_suffix(slug, dig=6):
    if not slug:
        return _slug_safety_filter(uuid.uuid4().hex[:dig])
    safe_len = 120 - 1 - dig  # make sure output slug is under 120 letter.
    return u'{}-{}'.format(slug[:safe_len], uuid.uuid4().hex[:dig])


def uuid4_hex(dig=32):
    return unicode(uuid.uuid4().hex[:dig])


def now(dig=10):
    if dig == 10:
        return int(time.time())
    elif dig == 11:
        return int(time.time() * 10)
    elif dig == 12:
        return int(time.time() * 100)
    elif dig == 13:
        return int(time.time() * 1000)
    elif dig == 14:
        return int(time.time() * 10000)
    elif dig == 15:
        return int(time.time() * 100000)
    elif dig == 16:
        return int(time.time() * 1000000)
    else:
        return time.time()


def numid():
    now_time = int(time.time() * 1000000)
    rand_int = random.randint(1, 9999)
    return u'{}{:04}'.format(now_time, rand_int)


def get_url_params(url, unique=True):
    if isinstance(url, str):
        url = url.decode('utf-8')

    result = urlparse.urlparse(url)
    params = urlparse.parse_qs(result.query, keep_blank_values=True)
    if unique:
        params = {k: v[-1] for k, v in params.iteritems()}
    return params


def add_url_params(url, input_params, unique=True, concat=True):
    if isinstance(url, str):
        url = url.decode('utf-8')

    if isinstance(input_params, dict):
        # make sure all value as list
        input_params = {k: v if isinstance(v, list) else [v]
                        for k, v in input_params.iteritems()}
    elif isinstance(input_params, basestring):
        input_params = {input_params: [u'']}
    else:
        return u''

    result = urlparse.urlparse(url)
    params = urlparse.parse_qs(result.query, keep_blank_values=True)

    if concat:
        for k, v in input_params.iteritems():
            if k in params:
                if isinstance(params[k], list):
                    params[k] += v
                else:
                    params[k] = [params[k]] + v
            else:
                params[k] = v
    else:
        params = input_params

    if unique:
        params = {k: v[-1] if unique else v for k, v in params.iteritems()}

    for k, v in params.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        elif isinstance(v, list):
            v = [i.encode('utf-8') if isinstance(i, unicode) else i
                 for i in v]
        params[k] = v

    result = list(result)
    try:
        params_str = urllib.urlencode(params, True)
        result[4] = params_str.replace('=&', '&').strip('=')
    except Exception as e:
        result[4] = str(e)

    return urlparse.urlunparse(result)


def get_pure_url(url):
    if url and isinstance(url, basestring):
        result = urlparse.urlparse(url)
        if not result.scheme:
            return u''
        return u'{r.scheme}://{r.netloc}{r.path}'.format(r=result)
    else:
        return u''


def get_url_path(url):
    if url and isinstance(url, basestring):
        result = urlparse.urlparse(url.strip('/')).path
        return result.strip('/')
    else:
        return u''


def get_url_domain(url):
    if isinstance(url, basestring):
        return urlparse.urlparse(url).netloc
    else:
        return u''


def gen_excerpt(raw_text, excerpt_length, ellipsis_mark=u'&hellip;'):
    excerpt = re.sub(r'<.*?>', '', raw_text).strip()
    excerpt_ellipsis = ellipsis_mark if len(excerpt) > excerpt_length else u''
    return u'{}{}'.format(excerpt[:excerpt_length], excerpt_ellipsis)


def safe_regex_str(val):
    if isinstance(val, str):
        val = val.decode('utf-8')
    elif not isinstance(val, unicode):
        return u''
    return re.sub(r'[\/\\*\.\[\]\(\)\^\|\{\}\?\$\!\@\#]', '', val)


def remove_multi_space(text):
    if isinstance(text, str):
        text = text.decode('utf-8')
    elif not isinstance(text, unicode):
        return u''
    return re.sub(r'\s+', u' ', text).replace('\n', u' ').replace('\b', u' ')


def parse_sortby(sort_by):
    key = None
    direction = None
    if isinstance(sort_by, basestring):
        if sort_by.startswith('+'):
            key = sort_by.lstrip('+')
            direction = 1
        else:
            key = sort_by.lstrip('-')
            direction = -1
    elif isinstance(sort_by, tuple):
        key = sort_by[0]
        direction = sort_by[1]
    else:
        return None
    return (key, direction)


def sortedby(source, sort_keys, reverse=False):
    if isinstance(sort_keys, (basestring, tuple)):
        sort_keys = [sort_keys]
    elif not isinstance(sort_keys, list):
        sort_keys = []

    sorts = [parse_sortby(key) for key in sort_keys]

    def compare(a, b):
        for sort in sorts:
            if sort is None:
                continue
            key = sort[0]
            direction = sort[1]
            if a.get(key) < b.get(key):
                return -1 * direction
            if a.get(key) > b.get(key):
                return 1 * direction
        return 0

    return sorted(source, key=cmp_to_key(compare), reverse=reverse)


def parse_int(num, default=0, natural=False):
    if not isinstance(default, int):
        default = 0
    if not isinstance(natural, (int, bool)):
        natural = False
    try:
        num = int(float(num))
    except (ValueError, TypeError):
        num = default
    if natural == 0:
        num = max(0, num)
    elif natural:
        num = max(1, num)
    return num


def parse_dict_by_structure(obj, structure):
    if not isinstance(obj, dict):
        obj = {}
    if isinstance(structure, list):
        structure = next(iter(structure), {})

    newobj = {}
    for k, v in structure.iteritems():
        val = obj.get(k)
        if v is ObjectId:
            if ObjectId.is_valid(val):
                newobj.update({k: ObjectId(val)})
            else:
                newobj.update({k: None})
        elif isinstance(v, list):
            if isinstance(val, list):
                newobj.update({k: [_val for _val in val if type(_val) in v]})
            else:
                newobj.update({k: []})
        else:
            if type(val) is v or v is None:
                newobj.update({k: val})
            else:
                try:
                    _val = v() if val is None else v(val)
                except Exception:
                    _val = v()
                newobj.update({k: _val})
    return newobj


def limit_dict(dict_obj, length=None):
    if not isinstance(dict_obj, dict):
        return {}
    elif not length or len(dict_obj) <= length:
        return dict(dict_obj)
    else:
        obj = {}
        for k, v in dict_obj.iteritems():
            if len(obj) < length:
                obj[k] = v
            else:
                break
        return obj


def _version_str_to_list(str_version):
    try:
        str_ver_list = str_version.split('.')[:4]
        version = [int(v) for v in str_ver_list[:3]]
        if len(str_ver_list) > 3:
            version.append(slugify(unicode(str_ver_list[3])))
    except Exception:
        version = None
    return version


def _version_list_to_str(list_version):
    try:
        # ensure has 3 items
        if len(list_version) < 3:
            for x in range(3 - len(list_version)):
                list_version.append(0)
        elif len(list_version) > 3:
            list_version[3] = slugify(unicode(list_version[3]))
        version = u'.'.join(map(unicode, list_version[:4]))
    except Exception:
        version = None
    return version


def version_str(ver):
    if isinstance(ver, basestring):
        ver = _version_str_to_list(ver)
    if isinstance(ver, list):
        ver = _version_list_to_str(ver)
    if not isinstance(ver, unicode):
        ver = u'0.0.0'
    return ver


def safe_filename(filename, mimetype=None):
    _starts = re.match(r'_*', filename)
    # this is for filename starts with one or many '_'

    if not mimetype:
        try:
            mimetype = mimetypes.guess_type(filename)[0]
        except Exception:
            mimetype = None

    filename = secure_filename(filename)
    name, ext = os.path.splitext(filename)
    if not name:
        time_now = int(time.time())
        name = u'unknow_filename_{}'.format(time_now)
    if not ext and mimetype:
        ext = mimetypes.guess_extension(mimetype)
        if not ext:
            ext = '.{}'.format(mimetype.split('/')[-1])
        if ext in ['.jpe']:  # keep jpg is jpg or jpeg.
            ext = '.jpg'
    filename = u'{}{}'.format(name, ext)
    return u'{}{}'.format(_starts.group(), filename)


def hmac_sha(key, msg, digestmod=None, output_hex=True):
    if digestmod is None:
        digestmod = hashlib.sha1
    sha = hmac.new(str(key), str(msg), digestmod=digestmod)
    if output_hex:
        return unicode(sha.hexdigest())
    else:
        return sha


def hmac_signature(key, payload, salt=u''):
    json_str = json.dumps(payload, sort_keys=True)
    sign_hash = unicode(hashlib.md5(json_str).hexdigest())
    try:
        salt = unicode(salt)
    except Exception:
        salt = u''
    msg = u'{}.{}'.format(sign_hash, salt)
    sha = hmac.new(str(key), str(msg))
    return unicode(sha.hexdigest())


def hash_md5(payload):
    json_str = json.dumps(payload, sort_keys=True)
    return unicode(hashlib.md5(json_str).hexdigest())


def parse_dateformat(date, to_format, input_datefmt='%Y-%m-%d'):
    if not to_format:
        return date
    if isinstance(date, basestring):
        try:
            date_object = datetime.strptime(date, input_datefmt)
        except Exception:
            return date
    elif isinstance(date, int):
        if len(str(int(date))) == 13:
            date = int(date / 1000)
        try:
            date_object = datetime.fromtimestamp(date)
        except Exception:
            return date
    else:
        return date

    try:
        if isinstance(to_format, unicode):
            to_format = to_format.encode('utf-8')
        _formatted = date_object.strftime(to_format)
        date_formatted = _formatted.decode('utf-8')
    except Exception:
        date_formatted = date
    return date_formatted


def to_timestamp(date, input_datefmt='%Y-%m-%d'):
    if isinstance(date, basestring):
        try:
            date = datetime.strptime(date, input_datefmt)
        except Exception:
            return 0
    elif not isinstance(date, datetime.datetime):
        return 0
    return int((date - datetime(1970, 1, 1)).total_seconds())


def time_age(date, gap=None, input_datefmt='%Y-%m-%d'):
    if not isinstance(gap, int):
        gap = 3600 * 24 * 365
    if isinstance(date, basestring):
        try:
            dt = datetime.strptime(date, input_datefmt)
            dt_stamp = (dt - datetime(1970, 1, 1)).total_seconds()
        except Exception:
            return None
    elif isinstance(date, int):
        if len(str(date)) == 13:
            date = int(date / 1000)
        dt_stamp = date
    elif isinstance(date, datetime.datetime):
        dt_stamp = (date - datetime(1970, 1, 1)).total_seconds()
    else:
        return None
    try:
        age = int(int(time.time()) - dt_stamp) / gap
    except Exception:
        return None
    return age


def str2unicode(text):
    if isinstance(text, str):
        return text.decode('utf-8')
    return text


def unicode2str(text):
    if isinstance(text, unicode):
        return text.encode('utf-8')
    return text


def match_cond(target, cond_key, cond_value, force=True, opposite=False):
    """
    params:
    - target: the source data want to check.
    - cond_key: the attr key of condition.
    - cond_value: the value of condition.
      if the cond_value is a list, any item matched will make output matched.
    - opposite: reverse check result.
    - force: must have the value or not.
    """

    def _dotted_get(key, obj):
        if not isinstance(obj, dict):
            return None
        elif '.' not in key:
            return obj.get(key)
        else:
            key_pairs = key.split('.', 1)
            obj = obj.get(key_pairs[0])
            return _dotted_get(key_pairs[1], obj)

    def _dotted_in(key, obj):
        if not isinstance(obj, dict):
            return False
        elif '.' not in key:
            return key in obj
        else:
            key_pairs = key.split('.', 1)
            obj = obj.get(key_pairs[0])
            return _dotted_in(key_pairs[1], obj)

    if cond_value == '' and not force:
        return _dotted_in(cond_key, target) != opposite
    elif cond_value is None and not force:
        # if cond_value is None will reverse the opposite,
        # then for the macthed opposite must reverse again. so...
        # also supported if the target value really is None.
        return _dotted_in(cond_key, target) == opposite
    elif isinstance(cond_value, bool) and not force:
        return _dotted_in(cond_key, target) != opposite
    elif not _dotted_in(cond_key, target):
        return False

    matched = False
    target_value = _dotted_get(cond_key, target)
    if isinstance(cond_value, list):
        for c_val in cond_value:
            matched = match_cond(target, cond_key, c_val, force=True)
            if matched:
                break
    elif isinstance(cond_value, bool):
        target_bool = isinstance(target_value, bool)
        matched = cond_value == target_value and target_bool
    else:
        if isinstance(target_value, list):
            matched = cond_value in target_value
        else:
            matched = cond_value == target_value

    return matched != opposite


def sorting_tags(tags, limit=60):
    tag_list = []
    tag_key_set = set()
    for tag in tags[:limit]:
        if not isinstance(tag, basestring):
            continue
        tag = tag.strip()
        key = tag.lower()
        if key not in tag_key_set:
            tag_key_set.add(key)
            tag_list.append(tag)
    return tag_list


def sorting_texts(texts, limit=60):
    return list(set([t for t in texts[:limit] if isinstance(t, unicode)]))


# str process
def str_contain(source, texts, contain_all=False):
    if isinstance(source, basestring):
        return None
    if isinstance(texts, basestring):
        texts = [texts]
    elif isinstance(texts, list):
        texts = [t for t in texts if isinstance(t, basestring)]
    else:
        return False

    matched_map = {}
    for t in texts:
        matched_map[t] = t in source

    if contain_all:
        return all(val for val in matched_map.values())
    else:
        return any(val for val in matched_map.values())


# mimetypes
def split_file_ext(filename):
    try:
        return os.path.splitext(filename)[1][1:].lower()
    except Exception:
        return None


def guess_file_type(filename, default=None, output_mimetype=True):
    try:
        guessed_type = mimetypes.guess_type(filename)[0]
    except Exception:
        guessed_type = None

    mimetype = guessed_type or default

    if not output_mimetype and mimetype:
        return mimetype.split('/')[0]
    else:
        return mimetype


# nonascii
def contains_nonascii_characters(string):
    """ check if the body contain nonascii characters"""
    for c in string:
        if not ord(c) < 128:
            return True
    return False


# random
def random_choices(seq, limit=1):
    seq = list(seq)
    selected = []

    def _random_item(seq):
        if not seq:
            return None
        rand = random.choice(seq)
        seq.remove(rand)
        return rand

    for i in xrange(limit):
        rand = _random_item(seq)
        if rand is not None:
            selected.append(rand)
        else:
            break
    return selected


def random_ascii_string(length=25):
    UNICODE_ASCII_CHARACTERS = (string.ascii_letters.decode('ascii') +
                                string.digits.decode('ascii'))
    r = random.SystemRandom()
    return ''.join([r.choice(UNICODE_ASCII_CHARACTERS)
                    for _ in xrange(length)])


def weighted_choice(source_list=None, weights=None):
    if not source_list:
        source_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    if not weights:
        weights = [19, 17, 15, 13, 11, 9, 7, 5, 3, 1]

    _diff = len(source_list) - len(weights)
    if _diff > 0:
        for _d in xrange(_diff):
            weights.append(0)
    elif _diff < 0:
        weights = weights[:len(source_list)]

    total = 0
    choose_idx = 0
    for i, w in enumerate(weights):
        total += w
        if random.random() * total < w:
            choose_idx = i
    return source_list[choose_idx]


# price
def convert_price(amount, use_currency=False, symbol=u'', fraction_size=2):
    pattern = u'{:,.{size}f}' if use_currency else u'{:.{size}f}'
    try:
        price = pattern.format(int(amount) / 100.0, size=fraction_size)
    except Exception:
        price = None
    return u'{}{}'.format(symbol, price)


# iter
def iter_product(args):
    # all possible of permutations and combinations for multiple list.
    def concat(x, y):
        _tmp = []
        for l in x:
            _l = tuple(l)
            for i in y:
                # concat list and item as tuple
                _tmp.append(_l + (i,))
        return _tmp

    return reduce(concat, args, [[]])


# uniquify a list of dict
def arrange_dicts(item_list):
    return [dict(d) for d in set(tuple(i.items()) for i in item_list)]


# chunks
def chunks(raw_list, group_size=12):
    for i in range(0, len(raw_list), max(group_size, 1)):
        yield raw_list[i:i + group_size]
