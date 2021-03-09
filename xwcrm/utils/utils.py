#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: utils.py
@time: 18/6/15 15:12
"""

import functools
import hashlib
import logging
import random
import socket
import struct
import time
from datetime import datetime

import chardet
import umsgpack
from passlib.hash import sha512_crypt
from requests.utils import get_encoding_from_headers, get_encodings_from_content


def quote_chinese(url, encodeing="utf-8"):
    if isinstance(url, unicode):
        return quote_chinese(url.encode("utf-8"))
    res = [b if ord(b) < 128 else '%%%02X' % (ord(b)) for b in url]
    return "".join(res)


def utf8(string):
    if isinstance(string, unicode):
        return string.encode('utf8')
    return string


md5string = lambda x: hashlib.md5(utf8(x)).hexdigest()

jinja_globals = {
    'md5': md5string,
    'quote_chinese': quote_chinese,
    'utf8': utf8,
    'timestamp': time.time,
}

list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "a",
        "b", "c", "d", "e", "f", "g", "h", "j", "k", "m", "n",
        "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "i", "l", "o", "z"]

def create_num_vali_code():
    n_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    rlist = random.sample(n_list, 6)
    return ''.join(str(e) for e in rlist)


def create_str_code():
    rlist = random.sample(list, 8)
    return ''.join(str(e) for e in rlist)


def create_n_s_code():
    n_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    s_list = ["a", "b", "c", "d", "e", "f", "g", "h", "j", "k", "m", "n", "p", "q", "r", "s", "t", "u", "v", "w", "x",
              "y", "i", "l", "o", "z"]
    rlist = random.sample(n_list, 1)
    llist = random.sample(s_list, 1)
    _list = random.sample(list, 6)
    mtr = ''.join(e for e in _list)
    rtr = ''.join(e for e in rlist)
    ltr = ''.join(e for e in llist)
    return ltr + mtr + rtr


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


def func_cache(f):
    _cache = {}

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        key = umsgpack.packb((args, kwargs))
        if key not in _cache:
            _cache[key] = f(*args, **kwargs)
        return _cache[key]

    return wrapper


def method_cache(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_cache'):
            self._cache = dict()
        key = umsgpack.packb((args, kwargs))
        if key not in self._cache:
            self._cache[key] = fn(self, *args, **kwargs)
        return self._cache[key]

    return wrapper


def find_encoding(content, headers=None):
    # content is unicode
    if isinstance(content, unicode):
        return 'unicode'
    encoding = None
    # Try charset from content-type
    if headers:
        encoding = get_encoding_from_headers(headers)
        if encoding == 'ISO-8859-1':
            encoding = None
    # Try charset from content
    if not encoding:
        encoding = get_encodings_from_content(content)
        encoding = encoding and encoding[0] or None
    # Fallback to auto-detected encoding.
    if not encoding and chardet is not None:
        encoding = chardet.detect(content)['encoding']
    if encoding and encoding.lower() == 'gb2312':
        encoding = 'gb18030'
    return encoding or 'latin_1'


def decode(content, headers=None):
    encoding = find_encoding(content, headers)
    if encoding == 'unicode':
        return content
    try:
        return content.decode(encoding, 'replace')
    except Exception as ex:
        logging.error(ex)
        return None


# 512位加密
def encrypt(text, encodeing="utf-8"):
    if text is None:
        return ""
    encrypt_text = sha512_crypt.hash(text)
    return encrypt_text


if __name__ == '__main__':
    print encrypt("87654321")


def verify(text, encrypt_text, encodeing="utf-8"):
    if (text is None) or (encrypt_text is None):
        return False
    res = sha512_crypt.verify(text, encrypt_text)
    return res


def parser_date(date, _format="%Y-%m-%d %H:%M:%S"):
    if not date or date == '':
        return ''
    datetime_object = datetime.strptime(date, _format)
    return datetime_object.strftime(_format)


def format_date(date, _format="%Y-%m-%d %H:%M:%S"):
    if not date or date == '':
        return ''
    return date.strftime(_format)


def timestamp_datetime(value):
    _format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(value)
    dt = time.strftime(_format, value)
    return dt


def datetime_timestamp(dt):
    _format = '%Y-%m-%d %H:%M:%S.%f'
    time.strptime(dt, _format)
    value = time.mktime(time.strptime(dt, _format))
    return int(value)
