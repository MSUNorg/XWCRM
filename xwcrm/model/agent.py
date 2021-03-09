#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: agent.py
@time: 18/6/20 17:33
"""

from models import DBDao, TAgent, TUser
from utils import utils
from utils.log_decorator import log_func_parameter

class TAgentDao(DBDao):
    """
    t_agent表操作
    """

    @log_func_parameter
    def add(self, uid, level, reward, status, parentid=None):
        """
        添加一条代理数据
        :param uid: 用户id
        :param level: 代理等级
        :param reward: 报酬
        :param status: 状态
        :param parentid:上级代理
        :return: 代理对象
        """
        agentid = utils.create_n_s_code()
        agent = TAgent(agentid, uid, level, reward, status, parentid)
        self._add(agent)
        return agent

    @log_func_parameter
    def update(self, agentid, update_dict):
        """
        已知代理id，跟新数据字典
        :param agentid: 代理id
        :param update_dict: 跟新数据字典
        :return:null
        """
        self.session.query(TAgent).filter(TAgent.agentid == agentid).update(update_dict, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update_uid(self, uid, update_dict):
        """
        已知用户id，更新数据字典
        :param uid:
        :param update_dict:
        :return:null
        """
        self.session.query(TAgent).filter(TAgent.uid == uid).update(update_dict, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def select_like(self, keyword):
        """
        使用关键字，查询用户id、用户名、代理id
        :param keyword: 关键字
        :return: 查询对象
        """
        res = self.session.query(TUser.uid, TUser.cname, TAgent.agentid).join(TAgent, TUser.uid == TAgent.uid).\
                filter(TUser.cname.like("%" + keyword + "%")).order_by(TAgent.createtime).all()
        return res

    @log_func_parameter
    def select_by_id(self, _agentid):
        """
        已知代理id，查询代理对象
        :param _agentid: 代理id
        :return: 代理对象
        """
        res = self.session.query(TAgent).filter(TAgent.agentid == _agentid).first()
        return res

    @log_func_parameter
    def select_by_uid(self, uid):
        """
        已知用户id，查询代理对象
        :param uid: 用户id
        :return: 代理对象
        """
        res = self.session.query(TAgent).filter(TAgent.uid == uid).first()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有代理
        :return: 所有代理对象
        """
        res = self.session.query(TAgent).order_by(TAgent.createtime).all()
        return res
