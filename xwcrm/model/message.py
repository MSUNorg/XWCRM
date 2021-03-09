#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: message.py
@time: 18/6/20 17:33
"""

from models import DBDao, TMessage, Pagination
from utils.log_decorator import log_func_parameter

class TMessageDao(DBDao):
    """
    t_message表操作
    """

    @log_func_parameter
    def add(self, msgtype, name, role_id, subject, body):
        """
        添加一条新消息
        :param msgtype:消息类型
        :param name:类型名称
        :param role_id:接收者
        :param subject:标题
        :param body:内容
        :return:消息对象
        """
        msg = TMessage(msgtype, name, role_id, subject, body)
        self._add(msg)
        return msg

    @log_func_parameter
    def search_page(self, msgtype, name, role_id, subject, page=None):
        """
        匹配参数，查询消息
        :param msgtype:类型
        :param name:类型名称
        :param role_id:接收者
        :param subject:标题
        :param page:内容
        :return: 切片后的消息对象
        """
        query = self.session.query(TMessage)
        if msgtype and msgtype != '' and msgtype != 'undefined':
            query = query.filter(TMessage.type == msgtype)
        if name and name != '' and name != 'undefined':
            query = query.filter(TMessage.name == name)
        if role_id and role_id != '' and role_id != 'undefined':
            query = query.filter(TMessage.role_id == role_id)
        if subject and subject != '' and subject != 'undefined':
            query = query.filter(TMessage.subject == subject)
        query.order_by(TMessage.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_by_msgtype(self, msgtype):
        """
        已知消息类型，查询消息对象
        :param msgtype: 消息类型
        :return: 消息对象
        """
        res = self.session.query(TMessage).filter(TMessage.type == msgtype).order_by(TMessage.createtime).first()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有消息
        :return: 消息对象
        """
        res = self.session.query(TMessage).order_by(TMessage.createtime).all()
        return res
