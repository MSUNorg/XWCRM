#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: menu.py
@time: 18/8/8 12:29
"""

import json
import logging
from model import role
from log_decorator import log_func_parameter

logger = logging.getLogger('xwcrm.menu')

@log_func_parameter
def _menu(utype):
    if utype == '终端客户':
        return '[{"title":"我的概况","children":[{"title":"我的首页","link":"/usermain","target":"_self"},{"title":"我的信息","link":"/customerinfo","target":"_self"},{"title":"身份验证","link":"/customerupdate","target":"_self"},{"title":"修改密码","link":"/updatepassword","target":"_self"},{"title":"退出系统","link":"quit","target":"_self"}]},{"title":"财务","children":[{"title":"入金存款","link":"/deposit","target":"_self"},{"title":"出金取款","link":"/withdrawmoney","target":"_self"},{"title":"账号之间转账","link":"/accounttransfer","target":"_self"},{"title":"出入金记录","link":"/historymoney","target":"_self"},{"title":"出金状态跟踪","link":"/depositfollowing","target":"_self"}]},{"title":"账户管理","children":[{"title":"交易账户","link":"/accountlist","target":"_self"},{"title":"我的客户","link":"/searchagent","target":"_self"},{"title":"我的网络","link":"/network","target":"_self"}]},{"title":"信息","children":[{"title":"MT5下载","link":"#","target":"_blank"}]}]'
    elif utype == '系统管理员':
        return '[{"title":"客服部门","children":[{"title":"任务","link":"/dashboard","target":"_self"},{"title":"消息","link":"/message","target":"_self"},{"title":"查找客户","link":"/searchcustomer?service","target":"_self"},{"title":"修改密码","link":"/updatepasswordbm","target":"_self"},{"title":"退出系统","link":"quit","target":"_self"}]},{"title":"代理部门","children":[{"title":"任务","link":"/dashboard","target":"_self"},{"title":"消息","link":"/message","target":"_self"},{"title":"查找客户","link":"/searchcustomer?agent","target":"_self"},{"title":"修改密码","link":"/updatepasswordbm","target":"_self"},{"title":"退出系统","link":"quit","target":"_self"}]},{"title":"系统管理员","children":[{"title":"用户管理","link":"/internaluserlist","target":"_self"},{"title":"角色管理","link":"/roleinfolist","target":"_self"},{"title":"工作流管理","link":"/workflowlist","target":"_self"},{"title":"分组管理","link":"/mtgroup","target":"_self"},{"title":"系统参数管理","link":"/sysparameter","target":"_self"},{"title":"修改密码","link":"/updatepasswordbm","target":"_self"},{"title":"退出系统","link":"quit","target":"_self"}]}]'
    else:
        return ''

@log_func_parameter
def menu(role_ids):
    roleDao = role.TRoleDao()
    menumap = roleDao.select_role_access(role_ids)
    items = menumap.items()
    items.sort()#A、B、...排序
    menuarray = []
    for key, value in items:
        menu = {}
        title = key
        children = []
        for obj in value:
            sub = {
                "title": obj.menu2,
                "link": obj.url,
                "target": obj.target
            }
            children.append(sub)
        list.sort(children,reverse=False)
        logger.info("children:%s",children)
        menu["title"] = title
        menu["children"] = children
        menuarray.append(menu)
    menustr = json.dumps(menuarray)
    logger.info(menustr)
    return menustr


if __name__ == '__main__':
    me = menu("customer")
    print json.loads(me)
