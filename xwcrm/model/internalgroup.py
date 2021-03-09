#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: internalgroup.py
@time: 18/6/20 17:33
"""

from models import DBDao, TGroup, Pagination
from utils.log_decorator import log_func_parameter

class TInternalGroupDao(DBDao):
    """
    t_group表操作
    """

    @log_func_parameter
    def select_all(self):
        """
        查询所有用户分组
        :return:
        """
        res = self.session.query(TGroup).order_by(TGroup.createtime).all()
        return res

