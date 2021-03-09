#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Zachary
# @license: commercial
# @contact:


import hashlib
import binascii
import random
from mt5_protocol import *


class MTUtils:

    @staticmethod
    def GetRandomHex(length):
        """
        Get random string hex format
        @param int length - length of string
        @return string
        """
        pass
        result = ''
        charlist = []
        for j in range(0, 16):
            charlist += hex(j)[2]
        # charlist = range(0, 10) + ['A', 'B', 'C', 'D', 'E']
        for i in range(0, length * 2):
            result += random.choice(charlist)
        #
        # for($i = 0 $i < $len $i++) $result .= sprintf("%02x", rand(0, 254))
        #
        return result

    @staticmethod
    def GetHashFromPassword(password, rand_code):
        """
        Get hash from password
        @param  string password  - user password
        @param string  rand_code - random string

        @return string
        """

        # 3 MD5 objects are needed
        h1 = hashlib.md5()
        h2 = hashlib.md5()
        h3 = hashlib.md5()
        # MD5(passwd)
        h1.update(password.encode('utf-16le'))
        # MD5(MD5(passwd)+'WebAPI')
        h2.update(binascii.a2b_hex(h1.hexdigest() + binascii.b2a_hex(MTProtocolConsts.WEB_API_WORD)))
        # hash of password
        password_hash = h2.hexdigest()
        # MD5(MD5(passwd)+'WebAPI'+SRV_RAND)
        h3.update(binascii.a2b_hex(password_hash + rand_code))
        # hash for answer
        return h3.hexdigest()
