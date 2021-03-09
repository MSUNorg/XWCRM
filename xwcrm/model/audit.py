#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: audit.py
@time: 18/6/20 17:33
"""

from models import DBDao, TAudit, Pagination
from utils.log_decorator import log_func_parameter

class TAuditDao(DBDao):
    """
    t_audit表操作
    """

    @log_func_parameter
    def select_all(self):
        """
        查询所有审计
        :return: 审计对象
        """
        res = self.session.query(TAudit).order_by(TAudit.createtime).all()
        return res