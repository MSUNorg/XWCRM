#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: tconfig.py
@time: 18/6/20 17:33
"""

from models import DBDao, TConfig
from utils.log_decorator import log_func_parameter

class TConfigQuery:
    def __init__(self):
        self.tconfigDao = TConfigDao()
        res = self.tconfigDao.select_all()
        config_dict = {}
        for obj in res:
            config_dict[obj.name] = obj.value
        self.config_dict = config_dict

    def get_by_name(self, name):
        return self.config_dict[name]

    @log_func_parameter
    def select_all(self):
        query = self.tconfigDao.select_all()
        return query


"""
https://xwcrm.bonusfx.cn/register?link=ABCD1234
select value from t_config where name ='代理链接地址' + select agentid from t_agent where uid=uid
"""


class TConfigDao(DBDao):
    """
    t_config表操作
    """

    @log_func_parameter
    def add(self, name, value, comment=""):
        """
        添加一条配置数据
        :param name:名字
        :param value: 值
        :param comment: 备注
        :return: 配置对象
        """
        tconfig = TConfig(name, value, comment)
        self._add(tconfig)
        return tconfig

    @log_func_parameter
    def update_value(self, name, value, comment=""):
        """
        已知name,更新value, comment=""
        :param name: 名字
        :param value: 值
        :param comment: 备注
        :return: null
        """
        self.session.query(TConfig).filter(TConfig.name == name).update({"value": value, "comment": comment},
                                                                        synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def select_by_name(self, name):
        """
        已知name，查询配置
        :param name: 名字
        :return: 配置对象
        """
        res = self.session.query(TConfig).filter(TConfig.name == name).first()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有配置对象
        :return: 配置对象
        """
        res = self.session.query(TConfig).all()
        return res

    @log_func_parameter
    def del_by_name(self, name):
        """
        已知name，删除该对象
        :param name: 名字
        :return: null
        """
        res = self.session.query(TConfig).filter(TConfig.name == name).first()
        self.session.delete(res)
        self.session.commit()
        self.session.close()
