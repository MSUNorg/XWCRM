#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: mtgroup.py
@time: 18/7/17 22:33
"""

from sqlalchemy import and_

from models import DBDao, TMTGroup, TMTGrouptype, Pagination

from utils.log_decorator import log_func_parameter

class TMTGroupDao(DBDao):
    """
    t_mtgroup表操作
    """

    @log_func_parameter
    def add(self, name, mtname, _type, spread, commission, leverage, maxbalance):
        """
        添加一条MT分组数据
        :param name: 组名
        :param mtname: mt名
        :param _type: 类型(1:标准组,2:专业组,3:VIP组,0:特殊组)
        :param spread: 内佣加点
        :param commission:外佣加点
        :param leverage:杠杆率
        :param maxbalance:资金上限
        :return:MT分组对象
        """
        mtgroup = TMTGroup(name, mtname, _type, spread, commission, leverage, maxbalance)
        self._add(mtgroup)
        return mtgroup

    @log_func_parameter
    def update(self, name, mtname, _type, spread, commission, leverage, maxbalance):
        """
        已知name，更新mtname, _type, spread, commission, leverage, maxbalance
        :param name: 组名
        :param mtname: mt名
        :param _type: 类型
        :param spread: 内佣加点
        :param commission: 外佣加点
        :param leverage: 杠杆率
        :param maxbalance: 资金上限
        :return:
        """
        self.session.query(TMTGroup).filter(TMTGroup.name == name).update(
            {"mtname": mtname, "type": _type, "spread": spread, "commission": commission, "leverage": leverage,
             "maxbalance": maxbalance},
            synchronize_session=False)
        self.session.commit()
        self.session.close()

    """
    mtgroup = select mtname from t_mtgroup where type=old_type
                 and leverage=old_leverage
                 and spread=new_spread
                 and commission=new_commission
    mtgroup为空则目标组合不存在
    """

    @log_func_parameter
    def select_mtname(self, old_type=1, new_spread=0, new_commission=0, old_leverage=300):
        """
        已知old_type, new_spread, new_commission, old_leverage，查询mtname
        :param old_type: 旧类型
        :param new_spread: 新内佣加点
        :param new_commission: 新外佣加点
        :param old_leverage: 旧杠杆率
        :return: mtname对象
        """
        res = self.session.query(TMTGroup.mtname).filter(and_(TMTGroup.type == old_type,
                                                              TMTGroup.leverage == old_leverage,
                                                              TMTGroup.spread == new_spread,
                                                              TMTGroup.commission == new_commission)).first()
        if not res:
            return "bonus\std\100L0r0c"
        return res.mtname

    @log_func_parameter
    def select_page(self, name, page=None):
        """
        已知name，分页查询MTGroup
        :param name: 分组名
        :param page: 分页
        :return: MTGroup对象
        """
        query = self.session.query(TMTGroup)
        if name and name != '' and name != 'undefined':
            query = query.filter(TMTGroup.name == name)
        query.order_by(TMTGroup.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_leverage(self):
        """
        查询杠杆率（不重复）
        :return: 杠杆率对象
        """
        res = self.session.query(TMTGroup.leverage).distinct(TMTGroup.leverage).all()
        return res

    # 加佣
    @log_func_parameter
    def select_commission(self):
        """
        查询外佣加点（不重复）
        :return: 外佣加点对象
        """
        res = self.session.query(TMTGroup.commission).distinct(TMTGroup.commission).all()
        return res

    # 加点
    @log_func_parameter
    def select_spread(self):
        """
        查询内佣加点（不重复）
        :return: 内佣加点对象
        """
        res = self.session.query(TMTGroup.spread).distinct(TMTGroup.spread).all()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有TMTGroup
        :return: 所有TMTGroup对象
        """
        res = self.session.query(TMTGroup).order_by(TMTGroup.createtime).all()
        return res

    @log_func_parameter
    def select_by_name(self, name):
        """
        已知name，查询TMTGroup
        :param name: 分组名
        :return: TMTGroup对象（一个）
        """
        res = self.session.query(TMTGroup).filter(TMTGroup.name == name).order_by(TMTGroup.createtime).first()
        return res

    @log_func_parameter
    def select_by_mtname(self, mtname):
        """
        已知mtname，查询TMTGroup
        :param mtname: mt名
        :return: TMTGroup对象（一个）
        """
        res = self.session.query(TMTGroup).filter(TMTGroup.mtname == mtname).order_by(TMTGroup.createtime).first()
        return res

    @log_func_parameter
    def del_by_name(self, name):
        """
        已知name，删除该条数据
        :param name: 分组名
        :return: null
        """
        res = self.session.query(TMTGroup).filter(TMTGroup.name == name).order_by(TMTGroup.createtime).first()
        self.session.delete(res)
        self.session.commit()
        self.session.close()


class TMTGrouptypeDao(DBDao):
    """
    t_mtgrouptype表操作
    """

    @log_func_parameter
    def select_new_user(self):
        """
        查询TMTGrouptype.type == 1时，TMTGrouptype.name
        :return: TMTGrouptype.name
        """
        # res = self.session.query(TMTGrouptype.name).filter(TMTGrouptype.type == 1).first()
        res = self.session.query(TMTGrouptype).filter(TMTGrouptype.type == 1).first()
        return res

    @log_func_parameter
    def select_inner(self):
        """
        查询TMTGrouptype.type > 1时，TMTGrouptype.name
        :return: TMTGrouptype.name
        """
        # res = self.session.query(TMTGrouptype.name).filter(TMTGrouptype.type > 1).first()
        res = self.session.query(TMTGrouptype).filter(TMTGrouptype.type > 1).first()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有TMTGrouptype
        :return: 所有TMTGrouptype
        """
        res = self.session.query(TMTGrouptype).all()
        return res
