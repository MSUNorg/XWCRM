#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: taskitem.py
@time: 18/6/20 17:33
"""

from models import DBDao, TTaskItem, Pagination
from utils.log_decorator import log_func_parameter

class TTaskItemDao(DBDao):
    """
    t_taskitem表操作
    """

    @log_func_parameter
    def add(self, t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points=None):
        """
        添加一条任务条款数据
        :param t_type: 类型
        :param o_uid: 发起人
        :param source_uid: 源用户
        :param target_uid: 目的用户
        :param sourcemt: 源MT账户
        :param targetmt: 目的MT账户
        :param mtgroup: MT分组
        :param state: 状态(queue=待审批, returned=被退回, finished=结束, reject=终⽌)
        :param tasknode_id: 当前节点
        :param amount: 金额
        :param exchange: 汇率
        :param points: 点数
        :return: 任务条款对象
        """
        taskitem = TTaskItem(t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points)
        self._add(taskitem)
        return taskitem

    @log_func_parameter
    def add_thin(self, t_type, o_uid, source_uid, target_uid, state, tasknode_id, points=None):
        """
        添加一条简单的任务条款数据
        :param t_type: 类型
        :param o_uid: 发起人
        :param source_uid: 源用户
        :param target_uid: 目的用户
        :param state: 状态
        :param tasknode_id: 当前节点
        :param points: 点数
        :return: 任务条款对象
        """
        taskitem = TTaskItem(t_type, o_uid, source_uid, target_uid, "", "", state, tasknode_id, points)
        self._add(taskitem)
        return taskitem

    @log_func_parameter
    def update(self, taskitem_id, state):
        """
        已知taskitem_id，更新state
        :param taskitem_id:任务条款id
        :param state:状态
        :return:null
        """
        self.session.query(TTaskItem).filter(TTaskItem.id == taskitem_id).update(
            {"state": state}, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update_t(self, taskitem_id, tasknode_id, state):
        """
        已知taskitem_id，更新tasknode_id, state
        :param taskitem_id: 任务条款id
        :param tasknode_id: 任务节点id
        :param state: 状态
        :return: null
        """
        self.session.query(TTaskItem).filter(TTaskItem.id == taskitem_id).update(
            {"tasknode_id": tasknode_id, "state": state},
            synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def search_page(self, task_type, o_uid, state, certid, page=None):
        """
        #TTaskItem.certid有这个字段么？
        已知task_type, o_uid, state, certid,查询任务条款
        :param task_type: 类型
        :param o_uid: 发起人
        :param state: 状态
        :param certid:
        :param page: 分页
        :return: 切片后的任务条款对象
        """
        query = self.session.query(TTaskItem)
        if task_type and task_type != '' and task_type != 'undefined':
            query = query.filter(TTaskItem.t_type == task_type)
        if o_uid and o_uid != '' and o_uid != 'undefined':
            query = query.filter(TTaskItem.o_uid == o_uid)
        if state and state != '' and state != 'undefined':
            query = query.filter(TTaskItem.state == state)
        if certid and certid != '' and certid != 'undefined':
            query = query.filter(TTaskItem.certid == certid)
        query.order_by(TTaskItem.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_by_id(self, taskitem_id):
        """
        已知taskitem_id，查询任务条款
        :param taskitem_id: 任务条款id
        :return: 任务条款对象
        """
        res = self.session.query(TTaskItem).filter(TTaskItem.id == taskitem_id).order_by(TTaskItem.createtime).first()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有任务条款
        :return: 多有任务条款对象
        """
        res = self.session.query(TTaskItem).order_by(TTaskItem.createtime).all()
        return res
