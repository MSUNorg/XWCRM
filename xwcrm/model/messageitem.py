#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: messageitem.py
@time: 18/6/20 17:33
"""

from models import DBDao, TMessageItem, Pagination
from utils.log_decorator import log_func_parameter

class TMessageItemDao(DBDao):
    """
    t_messageitem表操作
    """

    @log_func_parameter
    def add(self, m_type, o_uid, source_uid, target_id, sourcemt, targetmt, amount, points):
        """
        添加一条消息条款数据
        :param m_type: 类型
        :param o_uid:发起人
        :param source_uid:源用户
        :param target_id:目标用户
        :param sourcemt:源MT账户
        :param targetmt:目标MT账户
        :param amount:金额
        :param points:点数
        :return:消息条款对象
        """
        msgitem = TMessageItem(m_type, o_uid, source_uid, target_id, sourcemt, targetmt, amount, points)
        self._add(msgitem)
        return msgitem

    @log_func_parameter
    def search_page(self, m_type, o_uid, page=None):
        """
        匹配参数，查询消息条款
        :param m_type: 类型
        :param o_uid: 发起人
        :param page: 分页
        :return: 切片后的消息条款对象
        """
        query = self.session.query(TMessageItem)
        if m_type and m_type != '' and m_type != 'undefined':
            query = query.filter(TMessageItem.m_type == m_type)
        if o_uid and o_uid != '' and o_uid != 'undefined':
            query = query.filter(TMessageItem.o_uid == o_uid)
        query.order_by(TMessageItem.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_by_id(self, _id):
        """
        已知id，查询消息条款
        :param _id: 消息条款id
        :return: 消息条款对象
        """
        res = self.session.query(TMessageItem).filter(TMessageItem.id == _id).order_by(TMessageItem.createtime).first()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有消息条款
        :return: 消息条款对象
        """
        res = self.session.query(TMessageItem).order_by(TMessageItem.createtime).all()
        return res

