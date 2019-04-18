# coding=utf-8
from __future__ import absolute_import

import short_url
import random


def encode_short_url(length=6, case_sensitive=False):
    random_num = random.randint(0, len(short_url.DEFAULT_ALPHABET)**length)
    random_str = short_url.encode_url(random_num, length)
    if not case_sensitive:
        random_str = random_str.upper()
    return random_str


def decode_short_url(random_str, case_sensitive=False):
    if not random_str:
        return None
    if not case_sensitive:
        random_str = random_str.lower()
    return short_url.decode_url(random_str)


def short_code(length=6):
    end = len(short_url.DEFAULT_ALPHABET)**(length - 1)
    random_num = random.randint(0, end)
    return unicode(short_url.encode_url(random_num, length))
