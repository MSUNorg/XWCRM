#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: access.py
@time: 18/6/20 17:33
"""

from models import DBDao, TAccess, Pagination
from utils.log_decorator import log_func_parameter

class TAccessDao(DBDao):
    """
    t_access表操作
    """

    @log_func_parameter
    def add(self, name, url, _type, menu=False, element=None,  description=None):
        """
        添加一条权限数据
        :param name: 权限名
        :param url: url连接
        :param _type: 类型
        :param menu: 菜单
        :param element:元素
        :param description:说明
        :return:权限对象
        """
        role = TAccess(name, url, element, _type, menu, description)
        self._add(role)
        return role

    @log_func_parameter
    def update(self, accessId, element):
        """
        已知权限id，更新元素
        :param accessId: 权限id
        :param element: 元素
        :return: null
        """
        self.session.query(TAccess).filter(TAccess.id == accessId).update({"element": element},
                                                                          synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update(self, accessId, name, url):
        """
        已知权限id，更新权限名、权限url
        :param accessId: 权限id
        :param name: 权限名
        :param url: 权限url
        :return: null
        """
        self.session.query(TAccess).filter(TAccess.id == accessId).update({"name": name, "url": url},
                                                                          synchronize_session=False)
        self.session.commit()
        self.session.close()

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
    def select_menu(self):
        """
        查询菜单
        :return: 菜单对象
        """
        res = self.select_all()
        menumap = {}
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
    def select_by_name(self, name):
        """
        已知权限名，查询权限
        :param name:权限名
        :return:权限对象
        """
        if not name:
            return None
        res = self.session.query(TAccess).filter(TAccess.name == name).order_by(TAccess.createtime).first()
        return res

    @log_func_parameter
    def select_by_id(self, _id):
        """
        已知权限id，查询权限
        :param _id: 权限id
        :return: 权限对象
        """
        res = self.session.query(TAccess).filter(TAccess.id == _id).order_by(TAccess.createtime).first()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有权限
        :return: 权限对象
        """
        res = self.session.query(TAccess).order_by(TAccess.name).all()
        return res
