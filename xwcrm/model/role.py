#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: role.py
@time: 18/6/20 17:33
"""

import logging
from utils.utils import format_date
from models import DBDao, TRole, TAccess, Pagination
from utils.log_decorator import log_func_parameter

logger = logging.getLogger('xwcrm.role')

class TRoleDao(DBDao):
    """
    t_role表操作
    """

    @log_func_parameter
    def add(self, name, access, builtin, description=None):
        """
        添加一条角色数据
        :param name: 名称
        :param access: 权限
        :param builtin:系统角色boolean
        :param description:说明
        :return:角色对象
        """
        role = TRole(name, access, builtin, description)
        self._add(role)
        return role

    @log_func_parameter
    def update(self, role_id, name, access, description=None):
        """
        已知role_id，更新name, access, description
        :param role_id: 角色id
        :param name: 角色名称
        :param access: 权限
        :param description:说明
        :return: null
        """
        self.session.query(TRole).filter(TRole.id == role_id).update(
            {"name": name, "access": access, "description": description}, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def select_by_name(self, name, page=None):
        """
        已知name，查询角色
        :param name: 角色名称
        :param page: 分页
        :return: 角色对象
        """
        query = self.session.query(TRole)
        if name and name != '' and name != 'undefined':
            query = query.filter(TRole.name == name)
        query.order_by(TRole.createtime)
        if page == 0:
            return query.first()
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_by_id(self, _id):
        """
        已知id，查询角色
        :param _id: 角色id
        :return: 角色对象
        """
        _res = self.session.query(TRole).filter(TRole.id == _id).order_by(TRole.createtime).first()
        return _res

    """
    A / 123
    A / 456
    B / 001
    B / 002
    最终生成：
    A : [123, 456]
    B : [001, 002]
    当menu1为空的时候，此条目就不作为菜单项了
    """

    @log_func_parameter
    def select_role_access(self, _ids):
        """
        已知角色ids，查询有关所有菜单
        :param _ids: 角色ids
        :return: 菜单对象
        """
        _roles = self.session.query(TRole).filter(TRole.id.in_(_ids)).order_by(TRole.createtime).all()#获取角色对象
        access_ids = []
        for _role in _roles:
            for _access in _role.access:
                access_ids.append(_access)
        res = self.session.query(TAccess).distinct(TAccess.id).filter(TAccess.id.in_(access_ids)).order_by(
            TAccess.id).all()#获取权限对象
        #res = self.session.query(TAccess).filter(TAccess.id.in_(access_ids)).order_by(TAccess.id).all()
        menumap = {} #menumap = {'menu1A':[access_obj1,access_obj2,...],'menu1B':[access_obj3,...],...}
        for obj in res:
            menu1 = obj.menu1
            if not menu1:
                continue
            if menumap.has_key(menu1):
                menus = menumap[menu1]
                menus.append(obj)
            else:
                menus = [obj]
                menumap[menu1] = menus
        return menumap

    @log_func_parameter
    def select_all_access(self, _ids):
        """
        已知角色ids，查询有关所有权限
        :param _ids: 角色ids
        :return: 权限对象
        """
        _roles = self.session.query(TRole).filter(TRole.id.in_(_ids)).order_by(TRole.createtime).all()
        access_ids = []
        for _role in _roles:
            for _access in _role.access:
                access_ids.append(_access)
        res = self.session.query(TAccess).distinct(TAccess.id).filter(TAccess.id.in_(access_ids)).order_by(
            TAccess.id).all()
        _access = []
        for access in res:
            _access.append({
                "id": access.id,
                "name": access.name,
                "url": access.url,
                "element": access.element,
                "type": access.type,
                "menu1": access.menu1,
                "menu2": access.menu2,
                "target": access.target,
                "description": access.description,
                "createtime": format_date(access.createtime),
                "updatetime": format_date(access.updatetime)
            })
        return _access

    @log_func_parameter
    def select_all(self):
        """
        查询所有角色
        :return: 角色
        """
        res = self.session.query(TRole).order_by(TRole.createtime).all()
        return res

    @log_func_parameter
    def del_by_id(self, _id):
        """
        已知角色id，查询角色
        :param _id: 角色id
        :return: 角色
        """
        res = self.session.query(TRole).filter(TRole.id == _id).order_by(TRole.createtime).first()
        self.session.delete(res)
        self.session.commit()
        self.session.close()

