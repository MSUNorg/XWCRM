#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: redisToSession.py
@time: 18/7/8 15:12
"""

import hashlib
import uuid

import redis

from model import config


pool = redis.ConnectionPool(host=config.redis_host, port=config.redis_port)
conn = redis.Redis(connection_pool=pool)


class Sredis:
    Namespace = 'xwcrm'
    ExpiresTime = 60 * 20

    def __init__(self):
        pass

    @staticmethod
    def genkey():
        return str(uuid.uuid1()).replace('-', '')

    def setexpire(self, key, time):
        conn.expire(key, time)

    def __setitem__(self, key, value, time=604800):
        conn.hset(key, key, value)
        conn.expire(key, time)

    def __getitem__(self, key):
        ResultData = conn.hget(key, key)
        return ResultData

    def __delitem__(self, key):
        conn.hdel(key, key)


class Session:
    CookieID = 'uc'
    ExpiresTime = 60 * 20

    def __init__(self, handler):
        """
        用于创建用户session在redis中的字典
        :param handler: 请求头
        """
        self.handler = handler
        # 从客户端获取随机字符串
        SessionID = self.handler.get_secure_cookie(Session.CookieID, None)
        # 客户端存在并且在服务端也存在
        if SessionID and conn.exists(SessionID):
            self.SessionID = SessionID
        else:
            # 获取随机字符串
            self.SessionID = self.SessionKey()
            # 把随机字符串写入redis,时间是20分钟
            conn.hset(self.SessionID, None, None)
        # 每次访问超时时间就加20分钟
        conn.expire(self.SessionID, Session.ExpiresTime)
        # 设置Cookie
        self.handler.set_secure_cookie('uc', self.SessionID)

    def SessionKey(self):
        """
        :return: 生成随机字符串
        """
        UUID = str(uuid.uuid1()).replace('-', '')
        MD5 = hashlib.md5()
        MD5.update(bytes(UUID, encoding='utf-8'))
        SessionKey = MD5.hexdigest()
        return SessionKey

    def __setitem__(self, key, value):
        """
        :param key: session信息中的key
        :param value: 对应的Value
        """
        conn.hset(self.SessionID, key, value)

    def __getitem__(self, item):
        """
        :param item: Session信息中对应的Key
        :return: 获取的Session信息
        """
        # 获取对应的数据
        ResultData = conn.hget(self.SessionID, item)
        return ResultData

    def __delitem__(self, key):
        """
        :param key: 要删除的Key
        """
        conn.hdel(self.SessionID, key)

    def GetAll(self):
        # 获取Session中所有的信息，仅用于测试
        SessionData = conn.hgetall(self.SessionID)
        return SessionData
