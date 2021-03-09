#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: extpay.py
@time: 18/6/20 17:33
"""

from models import DBDao, TExtpay, Pagination
from utils.log_decorator import log_func_parameter

class TExtpayDao(DBDao):
    """
    t_extpay表操作
    """

    @log_func_parameter
    def select_all(self):
        """
        查询所有支付源对象
        :return: 支付源对象
        """
        res = self.session.query(TExtpay)
        return res