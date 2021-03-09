#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: test.py
@time: 18/6/15 14:23
"""

from model.models import *
from model import role, access, agent, user, views, fundflow
from utils import utils

userDao = user.UserDao()
roleDao = role.TRoleDao()
accessDao = access.TAccessDao()
agentDao = agent.TAgentDao()
fundflowDao = fundflow.TFundflowDao()
vmtuserDao = views.VMtuserDao()


# 手动创建角色
def create_role(name, _access, builtin):
    roleDao.add(name, _access, builtin)


# 手动创建权限
def create_access(name, url, _type):
    accessDao.add(name, url, _type)


# 创建渠道商
def create_agent(uid, level, reward):
    agentDao.add(uid, level, reward, status="0")


# 创建渠道商
def create_admin_user(cname, mobile, email, password):
    statusa = "正常"
    role_id = ["admin"]
    userDao.add(cname, mobile, email, utils.encrypt(password), "0", statusa, role_id)


def findfundflow():
    w = fundflowDao.select_by_uid("123445")
    print w.createtime
    print utils.datetime_timestamp(str(w.createtime))


if __name__ == '__main__':
    # init_db()  # 初始化数据库
    # drop_db()  # 删除数据库
    # create_agent("1112232322", "zxc", 1)
    # userDao.select_all()
    # findfundflow()
    pass
