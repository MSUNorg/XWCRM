#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: tasknode.py
@time: 18/6/20 17:33
"""

from models import DBDao, TTaskNode, Pagination
from sqlalchemy import and_
from utils.log_decorator import log_func_parameter

class TTaskNodeDao(DBDao):
    """
    t_tasknode表操作
    """

    @log_func_parameter
    def add(self, previous, name, t_type, approve, returned, step, canapprove, canreturn, canreject, role_id):
        """
        添加一条数据
        :param previous: 上一个节点ID
        :param name: 节点名称
        :param t_type: 所属Task类
        :param approve: approve命名
        :param returned: 被return命名
        :param step: 节点阶段
        :param canapprove: approve可用
        :param canreturn: return可用
        :param canreject: reject可用
        :param role_id: 处理者role
        :return: 任务节点对象
        """
        mtgroup = TTaskNode(previous, name, t_type, approve, returned, step, canapprove, canreturn, canreject, role_id)
        self._add(mtgroup)
        return mtgroup

    @log_func_parameter
    def update(self, _id, name, t_type, approve, returned, canapprove, canreturn, canreject, role_id):
        """
        已知任务节点id，跟新name, t_type, approve, returned, canapprove, canreturn, canreject, role_id
        未更新字段：previous、step
        :param _id: 任务节点id
        :param name: 任务节点名字
        :param t_type: 所属Task类
        :param approve: approve命名
        :param returned: 被return命名
        :param canapprove: approve可用
        :param canreturn: return可用
        :param canreject: reject可用
        :param role_id: 处理者role
        :return: null
        """
        self.session.query(TTaskNode).filter(TTaskNode.id == _id).update(
            {"name": name, "t_type": t_type, "approve": approve, "returned": returned, "canapprove": canapprove
                , "canreturn": canreturn, "canreturn": canreturn, "canreject": canreject, "role_id": role_id},
            synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def select_by_type_step(self, t_type, step):
        """
        已知t_type, step，查询任务节点
        :param t_type: 所属Task类
        :param step: 节点阶段
        :return: 任务节点对象
        """
        res = self.session.query(TTaskNode).filter(and_(TTaskNode.t_type == t_type, TTaskNode.step == step)).order_by(
            TTaskNode.createtime).first()
        return res

    @log_func_parameter
    def select_by_previous(self, previous):
        """
        已知previous，查询任务节点
        :param previous: 上一节点
        :return: 任务节点对象
        """
        res = self.session.query(TTaskNode).filter(TTaskNode.previous == previous).order_by(
            TTaskNode.createtime).first()
        return res

    @log_func_parameter
    def select_by_id(self, _id):
        """
        已知id，查询任务节点
        :param _id: 任务节点id
        :return: 任务节点对象
        """
        res = self.session.query(TTaskNode).filter(TTaskNode.id == _id).order_by(TTaskNode.createtime).first()
        return res

    @log_func_parameter
    def search_page(self, _type, page=None):
        """
        已知type，查询任务节点
        :param _type: 所属Task类
        :param page: 分页
        :return: 任务节点对象
        """
        query = self.session.query(TTaskNode)
        if _type and _type != '' and _type != 'undefined':
            query = query.filter(TTaskNode.t_type == _type)
        query.order_by(TTaskNode.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_all(self):
        """
        查询所有任务节点
        :return: 任务节点对象
        """
        res = self.session.query(TTaskNode).order_by(TTaskNode.createtime).all()
        return res

    @log_func_parameter
    def del_by_id(self, _id):
        """
        已知id，删除该任务节点对象
        :param _id: 任务节点id
        :return: null
        """
        res = self.session.query(TTaskNode).filter(TTaskNode.id == _id).order_by(TTaskNode.createtime).first()
        self.session.delete(res)
        self.session.commit()
        self.session.close()
