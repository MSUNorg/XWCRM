#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: fundflow.py
@time: 18/6/20 17:33
"""

import logging

from sqlalchemy import desc, func, or_, distinct

from models import DBDao, TFundflow, TFundtype, Pagination
from utils.log_decorator import log_func_parameter

logger = logging.getLogger('xwcrm.dao')


class TFundflowDao(DBDao):
    """
    t_fundflow表操作
    """

    @log_func_parameter
    def add(self, uid, _type, mtlogin, transaction, extorder, comment, extpay_id, exchange, credit=0, debit=0):
        """
        添加一条客户资金变动数据
        :param uid: 用户id
        :param _type: 类型
        :param mtlogin: MT账户
        :param transaction: 交易号
        :param extorder: 第三方单号
        :param comment:备注
        :param extpay_id:支付源
        :param exchange:汇率
        :param credit: 借
        :param debit: 贷
        :return: 资金变动对象
        """
        fundflow = TFundflow(uid, _type, mtlogin, transaction, extorder, comment, extpay_id, exchange, credit, debit)
        self._add(fundflow)
        return fundflow

    @log_func_parameter
    def add_with_id(self, _id, uid, _type, mtlogin, transaction, extorder, comment, extpay_id):
        """
        指定单号，添加一条客户资金变动数据
        :param _id:单号
        :param uid:用户id
        :param _type:类型
        :param mtlogin:MT账户
        :param transaction:交易号
        :param extorder:第三方单号
        :param comment:备注
        :param extpay_id:支付源
        :return:资金流动对象
        """
        fundflow = TFundflow(uid, _type, mtlogin, transaction, extorder, comment, extpay_id, 0, 0, _id)
        self._add(fundflow)
        return fundflow

    @log_func_parameter
    def update_amount(self, _id, _type, extorder, comment, credit, debit):
        """
        已知单号，更新类型、第三方单号、评论、借、贷
        :param _id:单号
        :param _type:类型
        :param extorder:第三方单号
        :param comment:评论
        :param credit:借
        :param debit:贷
        :return:null
        """
        self.session.query(TFundflow).filter(TFundflow.id == _id).update({"type": _type, "extorder": extorder,
                                                                          "comment": comment, "credit": credit,
                                                                          "debit": debit}, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def select_by_params_page(self, uid, mtlogin, opttype, start, end, page=None):
        """
        已知用户id、MT账户、操作类型，查询资金流动对象
        :param uid: 用户id
        :param mtlogin: MT账户
        :param opttype: 操作类型
        :param start: 开始
        :param end: 结束
        :param page:分页
        :return:切片后的资金流动对象
        """
        query = self.session.query(TFundflow).filter(TFundflow.uid == uid)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(TFundflow.mtlogin == mtlogin)
        if opttype and opttype != '' and opttype != 'undefined':
            query = query.filter(TFundflow.type == opttype)
        if start and start != '' and start != 'undefined':
            query = query.filter(TFundflow.createtime >= start)
        if end and end != '' and end != 'undefined':
            query = query.filter(TFundflow.createtime <= end)
        query.order_by(TFundflow.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_balance(self, uid):
        """
        已知客户id，查询借贷差额
        :param uid:用户id
        :return:差额
        """
        _credit = self.session.query(func.sum(TFundflow.credit)).filter(TFundflow.uid == uid).filter(
            or_(TFundflow.type == 10, TFundflow.type == 11, TFundflow.type == 31, TFundflow.type == 50,
                TFundflow.type == 51, TFundflow.type == 20, TFundflow.type == 21)).scalar()
        _debit = self.session.query(func.sum(TFundflow.debit)).filter(TFundflow.uid == uid).filter(
            or_(TFundflow.type == 10, TFundflow.type == 11, TFundflow.type == 31, TFundflow.type == 50,
                TFundflow.type == 51, TFundflow.type == 20, TFundflow.type == 21)).scalar()
        logger.error("_credit=%s,_debit=%s", _credit, _debit)
        if not _credit or ((not _debit) and _debit != 0):
            return 0
        amount = _credit - _debit
        return amount

    @log_func_parameter
    def select_by_id(self, _id):
        """
        已知单号，查询资金流动
        :param _id: 单号
        :return: 资金流动对象
        """
        res = self.session.query(TFundflow).filter(TFundflow.id == _id).order_by(TFundflow.createtime).first()
        return res

    @log_func_parameter
    def select_by_uid(self, _uid):
        """
        已知用户id，查询资金流动
        :param _uid: 用户id
        :return: 资金流动对象
        """
        res = self.session.query(TFundflow).filter(TFundflow.uid == _uid).order_by(desc(TFundflow.createtime)).first()
        return res

    @log_func_parameter
    def select_types_by_uid_distinct(self, _uid):
        """
        已知用户id，查询资金流动
        :param _uid: 用户id
        :return: 资金流动对象
        """
        query = self.session.query(TFundflow.type).distinct().filter(TFundflow.uid == _uid).all()
        # 形式[(11,), (20,), (21,), (30,), (51,)]
        res = []
        for e in query:
            res.append(e.type)
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有资金流动
        :return: 资金流动对象
        """
        res = self.session.query(TFundflow).order_by(TFundflow.createtime).all()
        return res


class TFundtypeDao(DBDao):
    """
    t_fundtype表操作
    """

    @log_func_parameter
    def select_all(self):
        """
        查询所有资金变动类型
        :return: 资金变动类型对象
        """
        res = self.session.query(TFundtype).all()
        return res
