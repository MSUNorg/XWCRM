#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: taskhistory.py
@time: 18/6/20 17:33
"""

from models import DBDao, TTaskHistory, Pagination
from utils.log_decorator import log_func_parameter

class TTaskHistoryDao(DBDao):
    """
    t_taskhistory表操作
    """

    @log_func_parameter
    def add(self, taskitem, oprator, change, tasknode_id, comment):
        """
        添加一条数据
        :param taskitem: 任务条款id
        :param oprator: 操作者
        :param change: 状态改变 state:{"new", "approve", "returned", "reject"}
        :param tasknode_id: 节点id
        :param comment: 备注
        :return: 任务历史对象
        """
        history = TTaskHistory(taskitem, oprator, change, tasknode_id, comment)
        self._add(history)
        return history

    @log_func_parameter
    def select_by_tid(self, taskitem_id):
        """
        已知taskitem_id，查询任务历史
        :param taskitem_id: 任务条款id
        :return: 任务历史对象
        """
        res = self.session.query(TTaskHistory).filter(TTaskHistory.taskitem == taskitem_id).order_by(TTaskHistory.createtime).all()
        return res

    @log_func_parameter
    def select_by_id(self, _id):
        """
        已知任务历史id，查询任务历史
        :param _id: 任务历史id
        :return: 任务历史对象
        """
        res = self.session.query(TTaskHistory).filter(TTaskHistory.id == _id).order_by(TTaskHistory.createtime).all()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有任务历史
        :return: 所有任务历史对象
        """
        res = self.session.query(TTaskHistory).order_by(TTaskHistory.createtime).all()
        return res
