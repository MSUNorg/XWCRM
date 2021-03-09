#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: innerMedium.py
@time: 18/6/15 15:12
@description: 内部中间人操作/代理商专员
"""

from base import *


# 创建代理商
class AgentsCreateHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)
        reward = self.get_json_argument('reward', default=None)
        o_uid = self.current_user.uid

        if not uid:
            self.error(u'请输入用户ID')
            return
        if not reward:
            self.error(u'请输入代理返佣')
            return
        _user = self.userDao.select_by_uid(uid)
        if not _user:
            self.error(u'请输入用户ID')
            return

        # 写入t_taskitem表
        _task = self.taskDao.select_by_trigger("/md/agents/create")
        if not _task:
            self.error(u'任务不存在')
            return
        t_type = _task.type
        _tasknode = self.tasknodeDao.select_by_type_step(t_type, 1)
        if not _tasknode:
            self.error(u'节点不存在')
            return
        tn_id = _tasknode.id
        # t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points
        _taskitem = self.taskitemDao.add(t_type, o_uid, uid, uid, "", "", None, "queue", tn_id, 0, 0, reward)
        # 写入t_taskhistory表
        self.taskhistoryDao.add(_taskitem.id, o_uid, "new", tn_id, "new")
        self.success(u'操作成功')
        return


# 修改代理商
class AgentsUpdateHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)
        reward = self.get_json_argument('reward', default=None)
        parent_uid = self.get_json_argument('parent_uid', default=None)
        o_uid = self.current_user.uid

        if not uid:
            self.error(u'请输入用户ID')
            return
        if not reward:
            self.error(u'请输入代理返佣')
            return
        if not parent_uid:
            self.error(u'请输入上级代理用户ID')
            return
        if parent_uid == uid:
            self.error(u'上级代理用户ID不正确')
            return
        _user = self.userDao.select_by_uid(uid)
        if not _user:
            self.error(u'请输入用户ID')
            return
        parent_user = self.userDao.select_by_uid(parent_uid)
        if not parent_user:
            self.error(u'请输入上级代理用户ID')
            return

        # 写入t_taskitem表
        _task = self.taskDao.select_by_trigger("/md/agents/update")
        if not _task:
            self.error(u'任务不存在')
            return
        t_type = _task.type
        _tasknode = self.tasknodeDao.select_by_type_step(t_type, 1)
        if not _tasknode:
            self.error(u'节点不存在')
            return
        tn_id = _tasknode.id
        # t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points
        _taskitem = self.taskitemDao.add(t_type, o_uid, uid, parent_uid, "", "", None, "queue", tn_id, 0, 0, reward)
        # 写入t_taskhistory表
        self.taskhistoryDao.add(_taskitem.id, o_uid, "new", tn_id, "new")
        self.success(u'操作成功')
        return


# 修改交易账户分组
class MTGroupUpdateHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        _mtgroup = self.get_json_argument('mtgroup', default=None)
        o_uid = self.current_user.uid

        if not uid:
            self.error(u'请输入用户ID')
            return
        if not mtlogin:
            self.error(u'请输入MT账号')
            return
        if not _mtgroup:
            self.error(u'请输入MT分组')
            return
        _user = self.userDao.select_by_uid(uid)
        if not _user:
            self.error(u'请输入用户ID')
            return

        # 写入t_taskitem表
        _task = self.taskDao.select_by_trigger("/md/mtgroup/update")
        if not _task:
            self.error(u'任务不存在')
            return
        t_type = _task.type
        _tasknode = self.tasknodeDao.select_by_type_step(t_type, 1)
        if not _tasknode:
            self.error(u'节点不存在')
            return
        tn_id = _tasknode.id
        # t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points
        _taskitem = self.taskitemDao.add(t_type, o_uid, uid, uid, mtlogin, mtlogin, _mtgroup, "queue", tn_id, 0, 0)
        # 写入t_taskhistory表
        self.taskhistoryDao.add(_taskitem.id, o_uid, "new", tn_id, "new")
        self.success(u'操作成功')
        return


# 修改客户代理
class AgentsCustomerUpdateHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        agent_uid = self.get_json_argument('agent_uid', default=None)
        o_uid = self.current_user.uid

        if not uid:
            self.error(u'请输入用户ID')
            return
        if not mtlogin:
            self.error(u'请输入MT账号')
            return
        if not agent_uid:
            self.error(u'请输入代理商用户ID')
            return
        _user = self.userDao.select_by_uid(uid)
        agent_user = self.userDao.select_by_uid(agent_uid)
        if not _user:
            self.error(u'请输入用户ID')
            return
        if not agent_user:
            self.error(u'请输入代理商用户ID')
            return

        # 写入t_taskitem表
        _task = self.taskDao.select_by_trigger("/md/agents/customer/update")
        if not _task:
            self.error(u'任务不存在')
            return
        t_type = _task.type
        _tasknode = self.tasknodeDao.select_by_type_step(t_type, 1)
        if not _tasknode:
            self.error(u'节点不存在')
            return
        tn_id = _tasknode.id
        # t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points
        _taskitem = self.taskitemDao.add(t_type, o_uid, uid, agent_user.uid, "", "", None, "queue", tn_id, 0, 0)
        # 写入t_taskhistory表
        self.taskhistoryDao.add(_taskitem.id, o_uid, "new", tn_id, "new")
        self.success(u'操作成功')
        return


# 代理商搜索
class AgentsSearchHandler(ApiHandler):
    def post(self):
        keyword = self.get_json_argument('keyword', default=None)
        if not keyword:
            self.error(u'请输入关键词查询')
            return
        # TUser.uid, TUser.cname, TAgent.agentid
        res = self.agentDao.select_like(keyword)
        _objs = []
        for obj in res:
            _objs.append({"agent_uid": str(obj.uid), "agent_cname": obj.cname, "agentid": str(obj.agentid)})
        self.suc(_objs)

handlers = [
    (r"/md/agents/create", AgentsCreateHandler),
    (r"/md/agents/update", AgentsUpdateHandler),
    (r"/md/agents/customer/update", AgentsCustomerUpdateHandler),
    (r"/md/mtgroup/update", MTGroupUpdateHandler),
    (r"/md/agents/search", AgentsSearchHandler),


]
