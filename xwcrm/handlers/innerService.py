#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: innerService.py
@time: 18/6/15 15:12
@description: 内部客服操作
"""

from base import *
from utils.utils import parser_date, format_date
import logging
logger = logging.getLogger("xwcrm.innerService")

# 任务类型查询
class TaskNameHandler(ApiHandler):
    def get(self):
        items = self.vtaskitemDao.select_taskname()
        _objs = []
        for obj in items:
            _objs.append({"task_type": obj.taskname})
        self.suc(_objs)
        return


# 待处理的任务
class TaskSearchHandler(ApiHandler):
    def post(self):
        task_type = self.get_json_argument('task_type', default=None)
        o_cname = self.get_json_argument('o_cname', default=None)
        page = self.get_json_argument('page', default=None)

        _user = self.current_user
        role_ids = _user.role_id
        logger.error("role_ids=%s", role_ids)
        # task_type, o_uid, state, o_cname, role_ids, page
        pagination = self.vtaskitemDao.select_page(task_type, None, -1, o_cname, role_ids, page)
        _objs = []
        for obj in pagination.items:
            _objs.append(
                {"id": obj.id, "subject": obj.subject, "taskname": obj.taskname, "body": obj.body, "o_uid": obj.o_uid,
                 "o_cname": obj.o_cname, "source_uid": obj.source_uid, "source_cname": obj.source_cname,
                 "target_uid": obj.target_uid, "target_cname": obj.target_cname, "sourcemt": obj.sourcemt,
                 "targetmt": obj.targetmt, "mtgroup": obj.mtgroup, "amount": "{:.6f}".format(obj.amount),
                 "exchange": "{:.6f}".format(obj.exchange), "points": obj.points,
                 "state": obj.state, "tasknode_id": obj.tasknode_id, "createtime": format_date(obj.createtime),
                 "updatetime": format_date(obj.updatetime),
                 "nodename": obj.nodename, "step": obj.step, "approve": obj.approve, "returned": obj.returned,
                 "canapprove": obj.canapprove, "canreturn": obj.canreturn, "canreject": obj.canreject,
                 "role_id": obj.role_id})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 我发起的任务
class MyTaskSearchHandler(ApiHandler):
    def post(self):
        task_type = self.get_json_argument('task_type', default=None)
        state = self.get_json_argument('state', default=None)
        page = self.get_json_argument('page', default=None)

        o_uid = self.current_user.uid
        pagination = self.vtaskitemDao.select_page(task_type, o_uid, state, None, None, page)
        _objs = []
        for obj in pagination.items:
            _objs.append(
                {"id": obj.id, "subject": obj.subject, "taskname": obj.taskname, "body": obj.body, "o_uid": obj.o_uid,
                 "o_cname": obj.o_cname, "source_uid": obj.source_uid, "source_cname": obj.source_cname,
                 "target_uid": obj.target_uid, "target_cname": obj.target_cname, "sourcemt": obj.sourcemt,
                 "targetmt": obj.targetmt, "mtgroup": obj.mtgroup, "amount": "{:.6f}".format(obj.amount),
                 "exchange": "{:.6f}".format(obj.exchange), "points": obj.points,
                 "state": obj.state, "tasknode_id": obj.tasknode_id, "createtime": format_date(obj.createtime),
                 "updatetime": format_date(obj.updatetime),
                 "nodename": obj.nodename, "step": obj.step, "approve": obj.approve, "returned": obj.returned,
                 "canapprove": obj.canapprove, "canreturn": obj.canreturn, "canreject": obj.canreject,
                 "role_id": obj.role_id})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 任务历史
class TaskHistoryHandler(ApiHandler):
    def post(self):
        taskitem_id = self.get_json_argument('taskitem_id', default=None)

        items = self.taskhistoryDao.select_by_tid(taskitem_id)
        _objs = []
        if not items:
            self.suc(_objs)
            return

        userall = self.userDao.select_all()
        userdic = {}
        for _user in userall:
            userdic[_user.uid] = _user.cname
        for obj in items:
            oprator_name = userdic[obj.oprator]
            _objs.append({"id": obj.id, "taskitem_id": obj.taskitem, "oprator": obj.oprator,
                          "oprator_name": oprator_name, "change": obj.change, "tasknode_id": obj.tasknode_id,
                          "comment": obj.comment, "createtime": format_date(obj.createtime)})
        self.suc(_objs)
        return


# 任务修改
class TaskUpdateHandler(ApiHandler):
    def post(self):
        taskitem_id = self.get_json_argument('taskitem_id', default=None)
        # 状态(approve, returned, reject)
        state = self.get_json_argument('state', default=None)
        comments = self.get_json_argument('comments', default=None)

        if not taskitem_id:
            self.error(u'请输入任务ID')
            return
        if not state:
            self.error(u'请输入任务状态')
            return
        if not comments:
            self.error(u'请输入任务注释')
            return

        _taskitem = self.taskitemDao.select_by_id(taskitem_id)
        if not _taskitem:
            self.error(u'任务不存在')
            return
        oprator = self.current_user.uid
        self.taskhistoryDao.add(taskitem_id, oprator, state, _taskitem.tasknode_id, comments)

        vti = self.vtaskitemDao.select_by_id(taskitem_id)
        if not vti:
            self.error(u'任务不存在')
            return
        tn_id = vti.tasknode_id
        try:
            if state == "approve":
                tn = self.tasknodeDao.select_by_previous(tn_id)
                method = vti.success
                if not tn or not tn.id:
                    self.taskitemDao.update(taskitem_id, "finished")
                    # 成功触发task.success
                    res = getattr(self.taskSuccess, method)(taskitem_id)
                    logger.info("approve method=%s,getattr_res=%s", method, res)
                    if res != '':
                        self.error(res)
                    else:
                        self.success(u'操作成功')
                    return
                else:
                    tasknode_id = tn.id
                    state = "queue"
                    self.taskitemDao.update_t(taskitem_id, tasknode_id, state)
                    self.success(u'操作成功')
                    return
            if state == "returned":
                tn = self.tasknodeDao.select_by_id(tn_id)
                previd = tn.previous
                tasknode_id = previd
                self.taskitemDao.update_t(taskitem_id, tasknode_id, state)
                self.success(u'操作成功')
                return
            if state == "reject":
                _taskitem = self.taskitemDao.select_by_id(taskitem_id)
                method = vti.fail
                self.taskitemDao.update_t(taskitem_id, _taskitem.tasknode_id, "reject")
                # 触发task.fail
                res = getattr(self.taskFail, method)(taskitem_id)
                logger.info("reject method=%s,getattr_res=%s", method, res)
                if res != '':
                    self.error(res)
                else:
                    self.success(u'操作成功')
                return
        except Exception as ex:
            logging.error(ex)
        self.error(u'操作失败')
        return


# 任务查看(未应用)
class TaskViewHandler(ApiHandler):
    def post(self):
        taskitem_id = self.get_json_argument('taskitem_id', default=None)
        if not taskitem_id:
            self.error(u'请输入任务ID')
            return

        obj = self.vtaskitemDao.select_by_id(taskitem_id)
        if not obj:
            self.error(u'任务不存在')
            return
        self.suc({"id": obj.id, "subject": obj.subject, "taskname": obj.taskname, "body": obj.body, "o_uid": obj.o_uid,
                  "o_cname": obj.o_cname, "source_uid": obj.source_uid, "source_cname": obj.source_cname,
                  "target_uid": obj.target_uid, "target_cname": obj.target_cname, "sourcemt": obj.sourcemt,
                  "targetmt": obj.targetmt, "mtgroup": obj.mtgroup, "amount": "{:.6f}".format(obj.amount),
                  "exchange": "{:.6f}".format(obj.exchange), "points": obj.points,
                  "state": obj.state, "tasknode_id": obj.tasknode_id, "createtime": format_date(obj.createtime),
                  "updatetime": format_date(obj.updatetime),
                  "nodename": obj.nodename, "step": obj.step, "approve": obj.approve, "returned": obj.returned,
                  "canapprove": obj.canapprove, "canreturn": obj.canreturn, "canreject": obj.canreject,
                  "role_id": obj.role_id})
        return


# 导出任务
class TaskExportHandler(ApiHandler):
    def post(self):
        task_type = self.get_json_argument('task_type', default=None)
        o_uid = self.get_json_argument('o_uid', default=None)
        state = self.get_json_argument('state', default=None)

        items = self.taskitemDao.search_page(task_type, o_uid, state, None, -1)
        _titles = ["t_type", "o_uid", "sourece_uid", "target_uid", "sourcemt", "targetmt", "state", "tasknode_id",
                   "amount", "exchange", "points", "createtime"]
        try:
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=customer.csv; charset=utf-8')
            self.write(','.join(_titles) + '\r\n')
            for obj in items:
                self.write(','.join([str(obj.t_type), str(obj.o_uid), str(obj.source_uid),
                                     str(obj.target_uid), str(obj.sourcemt), str(obj.targetmt), str(obj.state),
                                     str(obj.tasknode_id), str(obj.amount), str(obj.exchange), str(obj.points),
                                     format_date(obj.createtime)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 查询消息类型
class MessageTypeHandler(ApiHandler):
    def get(self):
        _user = self.current_user
        role_id = _user.role_id
        items = self.messageDao.search_page(None, None, role_id, None, -1)
        _objs = []
        for obj in items:
            _objs.append(
                {"msgtype": obj.type, "name": obj.name, "trigger": obj.trigger, "role_id": obj.role_id,
                 "subject": obj.subject, "body": obj.body, "createtime": format_date(obj.createtime),
                 "updatetime": format_date(obj.updatetime)})
        self.suc(_objs)
        return


# 个人消息查询
class MessageSearchHandler(ApiHandler):
    def post(self):
        msgtype = self.get_json_argument('msgtype', default=None)
        o_uid = self.get_json_argument('o_uid', default=None)
        page = self.get_json_argument('page', default=None)

        _user = self.current_user
        role_id = _user.role_id
        pagination = self.messageitemDao.search_page(msgtype, o_uid, page=page)
        msgtype_items = self.messageDao.search_page(None, None, role_id, None, -1)
        msgtype_dict = {}
        for msgtype_item in msgtype_items:
            msgtype_dict[str(msgtype_item.type)] = msgtype_item
        _objs = []
        for obj in pagination.items:
            _msgtype_item = msgtype_dict[str(obj.m_type)]
            _objs.append(
                {"id": obj.id, "name": _msgtype_item.name, "subject": _msgtype_item.subject, "body": _msgtype_item.body,
                 "m_type": obj.m_type, "o_uid": obj.o_uid, "source_uid": obj.source_uid,
                 "target_id": obj.target_id, "sourcemt": obj.sourcemt, "targetmt": obj.targetmt,
                 "amount": obj.amount, "points": obj.points, "createtime": format_date(obj.createtime)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 个人消息查看
class MessageViewHandler(ApiHandler):
    def get(self):
        msgitem_id = self.get_json_argument('id', default=None)

        if not msgitem_id:
            self.error(u'请输入消息ID')
            return
        _user = self.current_user
        role_id = _user.role_id
        obj = self.messageitemDao.select_by_id(msgitem_id)
        msgtype_items = self.messageDao.search_page(None, None, role_id, None, -1)
        msgtype_dict = {}
        for msgtype_item in msgtype_items:
            msgtype_dict[str(msgtype_item.type)] = msgtype_item
        _msgtype_item = msgtype_dict[str(obj.m_type)]
        self.suc(
            {"id": obj.id, "name": _msgtype_item.name, "subject": _msgtype_item.subject, "body": _msgtype_item.body,
             "m_type": obj.m_type, "o_uid": obj.o_uid, "source_uid": obj.source_uid,
             "target_id": obj.target_id, "sourcemt": obj.sourcemt, "targetmt": obj.targetmt,
             "amount": obj.amount, "points": obj.points, "createtime": format_date(obj.createtime)})
        return


# 导出消息
class MessageExportHandler(ApiHandler):
    def post(self):
        msgtype = self.get_json_argument('msgtype', default=None)
        o_uid = self.get_json_argument('o_uid', default=None)

        _user = self.current_user
        role_id = _user.role_id
        items = self.messageitemDao.search_page(msgtype, o_uid, page=-1)
        msgtype_items = self.messageDao.search_page(None, None, role_id, None, -1)
        msgtype_dict = {}
        for msgtype_item in msgtype_items:
            msgtype_dict[str(msgtype_item.type)] = msgtype_item
        _titles = ["id", "name", "subject", "body", "m_type", "o_uid", "source_uid", "target_id", "sourcemt",
                   "targetmt", "amount", "points", "createtime"]
        try:
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=customer.csv; charset=utf-8')
            self.write(','.join(_titles) + '\r\n')
            for obj in items:
                _msgtype_item = msgtype_dict[str(obj.m_type)]
                self.write(','.join([str(obj.id), str(_msgtype_item.name), str(_msgtype_item.subject),
                                     str(_msgtype_item.body), str(obj.m_type), str(obj.o_uid),
                                     str(obj.source_uid), str(obj.target_id), str(obj.sourcemt),
                                     str(obj.targetmt), str(obj.amount), str(obj.points),
                                     format_date(obj.createtime)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 内部客服——搜索客户
class CustomerSearchHandler(ApiHandler):
    def post(self):
        cname = self.get_json_argument('cname', default=None)
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        certid = self.get_json_argument('certid', default=None)
        bankaccount = self.get_json_argument('bankaccount', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        page = self.get_json_argument('page', default=None)
        agent_id = self.get_json_argument('agent_id', default=None)
        agent = self.get_json_argument('agent', default=None)

        pagination = self.vclientDao.search_page_join(cname, mobile, email, certid, mtlogin, agent_id, agent,
                                                      bankaccount, page)
        _objs = []
        for obj in pagination.items:
            mtloginstr = ','.join(str(e) for e in obj.mtlogin)
            # 代理商编码, 代理创建时间, 代理层级, 上级代理, 代理商状态
            _objs.append(
                {"uid": obj.uid, "cname": obj.cname, "mobile": obj.mobile, "email": obj.email, "certid": obj.certid,
                 "bankaccount": obj.bankaccount, "mtlogin": mtloginstr, "statusa": obj.statusa, "agent": obj.agent,
                 "agentid": obj.agentid, "parentid": obj.parentid, "level": obj.a_level, "status": obj.a_status,
                 "a_createtime": format_date(obj.a_createtime), "createtime": format_date(obj.createtime)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 内部客服——导出客户信息
class CustomerExportHandler(ApiHandler):
    def post(self):
        cname = self.get_json_argument('cname', default=None)
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        certid = self.get_json_argument('certid', default=None)
        bankaccount = self.get_json_argument('bankaccount', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        agent_id = self.get_json_argument('agent_id', default=None)
        agent = self.get_json_argument('agent', default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        page = -1

        pagination = self.vclientDao.search_page_join(cname, mobile, email, certid, mtlogin, agent_id, agent,
                                                      bankaccount, page)
        if version == "international":
            _titles = ["cname", "mobile", "email", "certid", "MT login", "status", "agent_code", "level", "parent_code",
                       "createtime"]
        else:
            _titles = ["姓名", "手机号", "邮箱", "证件号", "MT账号", "用户状态", "代理商编码", "代理商层级", "上级代理商编码",
                       "创建时间"]

        try:
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=customer.csv; charset=utf-8')
            self.write(','.join(_titles) + '\r\n')
            for obj in pagination:
                self.write(','.join([str(obj.cname), str(obj.mobile), str(obj.email), str(obj.certid),
                                     str(obj.mtlogin), str(obj.statusa), str(obj.agentid), str(obj.a_level),
                                     str(obj.agent), format_date(obj.createtime)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 查看客户基本信息
class CustomerViewHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)
        if not uid:
            self.error(u'请输入客户ID')
            return
        _user = self.userDao.select_by_uid(uid)
        if not _user:
            self.error(u'客户不存在')
            return

        _mtusers = self.vmtuserDao.select_by_uid(uid)
        _mt = []
        for mtuser in _mtusers:
            _mt.append(
                {"mtlogin": str(mtuser.mtlogin), "mtgroup": mtuser.mtgroup, "balance": "{:.6f}".format(mtuser.balance)})
        certpic0 = ""
        certpic1 = ""
        bankpic0 = ""
        addrpic0 = ""
        if _user.certpic0:
            certpic0 = config.view_path + _user.certpic0
        if _user.certpic1:
            certpic1 = config.view_path + _user.certpic1
        if _user.bankpic0:
            bankpic0 = config.view_path + _user.bankpic0
        if _user.addrpic0:
            addrpic0 = config.view_path + _user.addrpic0
        agent_id = _user.agent_id
        tconfig_value = self.configDao.get_by_name(u"代理链接地址")
        url = str(tconfig_value) + agent_id
        self.suc({"cname": _user.cname, "firstname": _user.firstname, "lastname": _user.lastname,
                  "mobile": _user.mobile, "email": _user.email, "certid": _user.certid, "bank": _user.bank,
                  "bankbranch": _user.bankbranch, "bankaccount": _user.bankaccount, "swiftcode": _user.swiftcode,
                  "agent_id": agent_id, "agent_url": url,
                  "statusa": _user.statusa, "certpic0": certpic0, "certpic1": certpic1, "bankpic0": bankpic0,
                  "certpic0_url": _user.certpic0, "certpic1_url": _user.certpic1, "bankpic0_url": _user.bankpic0,
                  "country": _user.country, "state": _user.state, "address": _user.address, "addrpic0": addrpic0,
                  "addrpic0_url": _user.addrpic0, "statusa": _user.statusa, "mt": _mt})
        return


# 修改客户基本信息
class CustomerUpdateHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)
        cname = self.get_json_argument('cname', default=None)
        firstname = self.get_json_argument('firstname', default='')
        lastname = self.get_json_argument('lastname', default='')
        certid = self.get_json_argument('certid', default=None)
        bank = self.get_json_argument('bank', default=None)
        bankbranch = self.get_json_argument('bankbranch', default=None)
        bankaccount = self.get_json_argument('bankaccount', default=None)
        swiftcode = self.get_json_argument('swiftcode', default=None)
        certpic0 = self.get_json_argument('certpic0', default=None)
        certpic1 = self.get_json_argument('certpic1', default=None)
        bankpic0 = self.get_json_argument('bankpic0', default=None)
        country = self.get_json_argument('country', default=None)
        state = self.get_json_argument('state', default=None)
        address = self.get_json_argument('address', default=None)
        addrpic0 = self.get_json_argument('addrpic0', default=None)
        statusa = self.get_json_argument('statusa', default=None)
        email = self.get_json_argument('email', default=None)
        mobile = self.get_json_argument('mobile', default=None)

        if not cname:
            if not firstname or not lastname:
                self.error(u'请输入客户名称')
                return
            cname = firstname + ' ' + lastname
        if not uid:
            self.error(u'请输入客户ID')
            return
        _user = self.userDao.select_by_uid(uid)
        if not _user:
            self.error(u'客户不存在')
            return
        self.userDao.update_profile(uid, cname, firstname, lastname, certid, bank, bankbranch, swiftcode, certpic0,
                                    certpic1, bankpic0, bankaccount, country, state, address, addrpic0, statusa, email,
                                    mobile)
        self.success("update success")
        return

# 新建交易账户
class MTCreateHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)

        if not uid:
            self.error(u'请输入客户ID')
            return
        _user = self.userDao.select_by_uid(uid)
        if not _user:
            self.error(u'请输入客户ID')
            return
        _mtusers = self.vmtuserDao.select_by_uid(_user.uid)
        if _user.statusa == u'集群':
            if len(_mtusers) >= 100:
                self.error(u'交易账户已达上限')
                return
        else:
            if len(_mtusers) >= 3:
                self.error(u'交易账户已达上限')
                return
        vmtuser = self.vmtuserDao.select_by_uid_first(uid)
        _mtlogin = self.vmtuserDao.select_max_login() + 1
        mtlogin = str(_mtlogin)
        mtpasswd = utils.create_str_code()
        mtgroupstr = vmtuser.mtgroup
        mtgroupstr = mtgroupstr.replace('\\', '\\\\')
        if not self.mtDao.doCreate(mtlogin, mtpasswd, mtgroup=mtgroupstr):
            self.error(u'内部错误')
            return

        mtlogins = _user.mtlogin
        mtls = []
        for mtuser in mtlogins:
            mtls.append(mtuser)
        mtls.append(mtlogin)
        self.userDao.update_mtloginids(_user.uid, mtls)
        _mt = [
            {"mtlogin": mtlogin, "mtpasswd": mtpasswd, "balance": 0}
        ]
        self.success("mt add success", {"mt": _mt})
        return


# 修改交易账户
class MTUpdateHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        _type = self.get_json_argument('type', default=None)
        leverage = self.get_json_argument('leverage', default=None)

        if not uid:
            self.error(u'请输入客户ID')
            return
        if not mtlogin:
            self.error(u'请输入账户')
            return
        if not _type:
            self.error(u'请输入类型')
            return
        if not leverage:
            self.error(u'请输入交易比例杠杆')
            return
        _user = self.userDao.select_by_uid(uid)
        if not _user:
            self.error(u'请输入客户ID')
            return

        if not self.mtDao.doGroup(mtlogin, leverage, _type):
            self.error(u'内部错误')
            return
        self.success()
        return


# 审批新建交易账户
class ApprovalMTCreateHandler(ApiHandler):
    def post(self):
        self.success(u'接口开发中')
        return


# 审批修改交易账户
class ApprovalMTUpdateHandler(ApiHandler):
    def post(self):
        self.success(u'接口开发中')
        return


# MT分组查询接口
class MTGroupSearchHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        if not mtlogin:
            self.error(u'请输入账户')
            return
        mtlogins = self.vmtuserDao.select_by_mtlogin(mtlogin)
        mtls = []
        for mtuser in mtlogins:
            mtls.append({"mtgroup": mtuser.mtgroup, "groupname": mtuser.groupname})
        self.success(u'success', mtls)
        return


# MT全部分组接口
class MTGroupALLHandler(ApiHandler):
    def post(self):
        mtgroups = self.mtgroupDao.select_all()
        objs = []
        for obj in mtgroups:
            objs.append({"name": obj.name, "mtname": obj.mtname})
        self.success(u'success', objs)
        return


# 内部客服——MT账户成交历史记录
class DealhistoryHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument("page", default=None)
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        if not uid:
            self.error(u'请输入用户ID')
        pagination = self.vdealhistoryDao.search_by_uid(uid, start, end, mtlogin, page)
        sum_list = self.vdealhistoryDao.searchsum_by_uid(uid, start, end, mtlogin)
        _objs = []  # 放一般数据
        for obj in pagination.items:
            _objs.append({"deal": str(obj.deal), "login": str(obj.login),
                          "action": str(obj.action), "entry": str(obj.entry),
                          "time": str(obj.time), "symbol": str(obj.symbol), "price": str(obj.price),
                          "volume": str("{:.2f}".format(obj.volume / 10000)), "profit": str(obj.profit),
                          "storage": str(obj.storage),
                          "profitraw": str(obj.profitraw), "positionid": str(obj.positionid),
                          "priceposition": str(obj.priceposition), "commission": str(obj.commission)
                          })

        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs, "sums": sum_list})


# 内部客服——MT账户成交历史记录导出
class DealhistoryExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = -1
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        if not uid:
            self.error(u'请输入用户ID')
        try:
            pagination = self.vdealhistoryDao.search_by_uid(uid, start, end, mtlogin, page)
            if not pagination:
                self.error(u'没有可导出的数据')
                return
            # sum_list = self.vdealhistoryDao.searchsum_by_uid(uid, start, end, mtlogin)
            self.set_header('Content-Type', 'application/octet-stream')  # 询问"打开”还是“保存"
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            if version == "international":
                self.write(
                    ",".join(["Time", "Deal", "Position", "MT login", "Symbol", "Action", "Entry", "Lot", "Price",
                              "PriceOpen", "Profit", "Storage", "Commission", "ProfitRaw"]) + "\r\n")
            else:
                self.write(
                    ",".join(
                        ["时间", "成交号", "飘单号", "MT账户", "品种", "类型", "方向", "交易量", "成交价", "开仓价", "利润", "库存费",
                         "手续费", "净利润"]) + "\r\n")
            for obj in pagination:
                self.write(",".join(
                    [str(obj.time), str(obj.deal), str(obj.login), str(obj.action), str(obj.entry), str(obj.symbol),
                     str(obj.price), str("{:.2f}".format(obj.volume / 10000)), str(obj.profit), str(obj.storage),
                     str(obj.profitraw), str(obj.positionid), str(obj.priceposition), str(obj.commission)]) + "\r\n")
            self.flush()
            return
        except Exception as e:
            logger.error(e)
            self.error("export csv file fail")
            return


# 内部客服——MT账户交易历史记录
class TradehistoryHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument("page", default=None)
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        if not uid:
            self.error(u'请输入用户ID')
        pagination = self.vtradehistoryDao.search_by_uid(uid, start, end, mtlogin, page)
        sum_list = self.vtradehistoryDao.searchsum_by_uid(uid, start, end, mtlogin)
        _objs = []
        for obj in pagination.items:
            _objs.append(
                {"o_time": str(obj.o_time), "o_deal": str(obj.o_deal), "login": str(obj.login),
                 "symbol": str(obj.symbol),
                 "o_action": str(obj.o_action), "volume": str("{:.2f}".format(obj.volume / 10000)),
                 "o_price": str(obj.o_price),
                 "o_commission": str(obj.o_commission),
                 "positionid": str(obj.positionid), "c_time": str(obj.c_time), "c_deal": str(obj.c_deal),
                 "volumeclosed": str("{:.2f}".format(obj.volumeclosed / 10000)), "c_price": str(obj.c_price),
                 "profit": str(obj.profit),
                 "storage": str(obj.storage),
                 "c_commission": str(obj.c_commission), "profitraw": str(obj.profitraw)})

        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs, "sums": sum_list})


# 内部客服——MT账户交易历史记录导出
class TradehistoryExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        page = -1
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        if not uid:
            self.error(u'请输入用户ID')
        try:
            pagination = self.vtradehistoryDao.search_by_uid(uid, start, end, mtlogin, page)
            if not pagination:
                self.error(u'没有可导出的数据')
                return
            # sum_list = self.vtradehistoryDao.searchsum_by_uid(uid, start, end, mtlogin)
            self.set_header('Content-Type', 'application/octet-stream')  # 询问"打开”还是“保存"
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            if version == "international":
                self.write(
                    ",".join(
                        ["TimeOpen", "DealOpen", "MT login", "Symbol", "Action", "LotOpen", "PriceOpen", "Comm.Open",
                         "Position", "TimeClose", "DealClose", "LotClose", "PriceClose", "Profit", "Storage",
                         "Comm.Close", "ProfitRaw"]) + "\r\n")
            else:
                self.write(
                    ",".join(
                        ["开仓时间", "开仓成交号", "MT账户", "品种", "类型", "开仓交易量", "开仓价", "手续费",
                         "飘单号", "平仓时间", "平仓成交号", "平仓交易量", "平仓价", "利润", "库存费",
                         "手续费", "净利润"]) + "\r\n")
            for obj in pagination:
                self.write(
                    ",".join([str(obj.o_time), str(obj.o_deal), str(obj.login), str(obj.symbol), str(obj.o_action),
                              str("{:.2f}".format(obj.volume / 10000)), str(obj.o_price), str(obj.o_commission),
                              str(obj.positionid), str(obj.c_time), str(obj.c_deal),
                              str("{:.2f}".format(obj.volumeclosed / 10000)), str(obj.c_price),
                              str(obj.profit), str(obj.storage), str(obj.c_commission),
                              str(obj.profitraw)]) + "\r\n")
            self.flush()
            return
        except Exception as e:
            logger.error(e)
            self.error("export csv file fail")
            return


# 内部客服——MT账户飘单记录
class OpenpositionHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument("page", default=None)
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        if not uid:
            self.error(u'请输入用户ID')
        pagination = self.vopenpositionDao.search_by_uid(uid, start, end, mtlogin, page)
        sum_list = self.vopenpositionDao.searchsum_by_uid(uid, start, end, mtlogin)
        _objs = []
        for obj in pagination.items:
            _objs.append(
                {"timecreate": str(obj.timecreate), "timeupdate": str(obj.timeupdate), "position": str(obj.position),
                 "login": str(obj.login), "symbol": str(obj.symbol), "action": str(obj.action),
                 "volume": str("{:.2f}".format(obj.volume / 10000)),
                 "priceopen": str(obj.priceopen), "pricesl": str(obj.pricesl), "pricetp": str(obj.pricetp),
                 "pricecurrent": str(obj.pricecurrent), "storage": str(obj.storage), "profit": str(obj.profit)})

        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs, "sums": sum_list})


# 内部客服——MT账户飘单记录导出
class OpenpositionExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        page = -1
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        if not uid:
            self.error(u'请输入用户ID')
        try:
            pagination = self.vopenpositionDao.search_by_uid(uid, start, end, mtlogin, page)
            if not pagination:
                self.error(u'没有可导出的数据')
                return
            # sum_list = self.vopenpositionDao.searchsum_by_uid(uid, start, end, mtlogin)
            self.set_header('Content-Type', 'application/octet-stream')  # 询问"打开”还是“保存"
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            if version == "international":
                self.write(",".join(["Time", "Update", "Position", "MT login", "Symbol", "Action",
                                     "Lot", "PriceOpen", "S/L", "T/P", "PriceCurrent", "Storage",
                                     "Profit"]) + "\r\n")
            else:
                self.write(",".join(["时间", "更新", "飘单号", "MT账户", "品种", "类型",
                                     "交易量", "开仓价", "止损", "止盈", "当前价", "库存费",
                                     "利润"]) + "\r\n")
            for obj in pagination:
                self.write(",".join([str(obj.timecreate), str(obj.timeupdate), str(obj.position),
                                     str(obj.login), str(obj.symbol), str(obj.action),
                                     str("{:.2f}".format(obj.volume / 10000)),
                                     str(obj.priceopen), str(obj.pricesl), str(obj.pricetp),
                                     str(obj.pricecurrent), str(obj.storage), str(obj.profit)]) + "\r\n")
            self.flush()
            return
        except Exception as e:
            logger.error(e)
            self.error("export csv file fail")
            return


# 内部客服——客户资金变动历史
class FinHistoryHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        opttype = self.get_json_argument('opttype', default=None)
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument('page', default=None)
        uid = self.get_json_argument('uid')

        if not uid:
            self.error(u'用户错误')
            return
        pagination = self.fundflowDao.select_by_params_page(uid, mtlogin, opttype, parser_date(start, "%Y-%m-%d"),
                                                            parser_date(end, "%Y-%m-%d"), page)
        fundtypes = self.fundtypeDao.select_all()
        fundtypemap = {}
        for ft in fundtypes:
            fundtypemap[ft.type] = ft.name

        extpays = self.extpayDao.select_all()
        extpaymap = {}
        for extpay in extpays:
            extpaymap[extpay.id] = extpay.name

        _objs = []
        for obj in pagination.items:

            if obj.extpay_id == '                                ':
                extpayname = ''
            elif obj.extpay_id == '' or obj.extpay_id is None:
                extpayname = ''
            else:
                extpayname = extpaymap[obj.extpay_id]
            _objs.append(
                {"id": str(obj.id), "type": obj.type, "typename": fundtypemap[obj.type], "mtlogin": str(obj.mtlogin),
                 "transaction": obj.transaction, "margin": "{:.2f}".format(obj.credit - obj.debit),
                 "comment": obj.comment,
                 "extorder": obj.extorder, "extpay": extpayname, "exchange": str(obj.exchange),
                 "createtime": format_date(obj.createtime)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 内部客服——客户资金变动历史导出
class FinHistoryExportHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        opttype = self.get_json_argument('opttype', default=None)
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        uid = self.get_json_argument('uid')
        version = self.get_json_argument('version', default=None)  # 国际版
        page = -1
        if not uid:
            self.error(u'用户错误')
            return
        try:
            pagination = self.fundflowDao.select_by_params_page(uid, mtlogin, opttype, parser_date(start, "%Y-%m-%d"),
                                                                parser_date(end, "%Y-%m-%d"), page)
            if not pagination:
                self.error(u'没有可导出的数据')
                return

            fundtypes = self.fundtypeDao.select_all()
            fundtypemap = {}
            for ft in fundtypes:
                fundtypemap[ft.type] = ft.name

            extpays = self.extpayDao.select_all()
            extpaymap = {}
            for extpay in extpays:
                extpaymap[extpay.id] = extpay.name

            self.set_header('Content-Type', 'application/octet-stream')  # 询问"打开”还是“保存"
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            if version == "international":
                self.write(",".join(
                    ["createtime", "typename", "MT login", "margin", "transaction", "extorder", "extpay",
                     "exchange", ]) + "\r\n")
            else:
                self.write(",".join(["操作日期", "操作类型", "交易账号", "金额", "交易单号", "第三方单号", "支付源", "汇率"]) + "\r\n")
            for obj in pagination:

                if obj.extpay_id == '                                ':
                    extpayname = ''
                elif obj.extpay_id == '' or obj.extpay_id is None:
                    extpayname = ''
                else:
                    extpayname = extpaymap[obj.extpay_id]

                self.write(",".join([format_date(obj.createtime), str(fundtypemap[obj.type]), str(obj.mtlogin),
                                     "{:.2f}".format(obj.credit - obj.debit), str(obj.transaction), str(obj.extorder),
                                     str(extpayname), str(obj.exchange), ]) + "\r\n")
            self.flush()
            return
        except Exception as e:
            logger.error(e)
            self.error("export csv file fail")
            return


# 电子钱包余额
class BalanceEwalletHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid')
        if not uid:
            self.error(u'用户错误')
            return
        amount = self.fundflowDao.select_balance(uid)
        self.suc({"amount": "{:.6f}".format(amount)})
        return


handlers = [
    (r"/cs/task/name", TaskNameHandler),
    (r"/cs/task/search", TaskSearchHandler),
    (r"/cs/task/search/my", MyTaskSearchHandler),

    (r"/cs/task/history", TaskHistoryHandler),
    (r"/cs/task/update", TaskUpdateHandler),
    (r"/cs/task/view", TaskViewHandler),
    (r"/cs/task/export", TaskExportHandler),

    (r"/cs/msg/type", MessageTypeHandler),
    (r"/cs/msg/search", MessageSearchHandler),
    (r"/cs/msg/view", MessageViewHandler),
    (r"/cs/msg/export", MessageExportHandler),

    (r"/cs/customer/search", CustomerSearchHandler),
    (r"/cs/customer/export", CustomerExportHandler),
    (r"/cs/customer/view", CustomerViewHandler),
    (r"/cs/customer/update", CustomerUpdateHandler),
    # (r"/cs/customer/tradehistory", CustomerTradehistoryHandler),

    (r"/cs/mt/create", MTCreateHandler),
    (r"/cs/mt/update", MTUpdateHandler),
    (r"/cs/mt/create/approval", ApprovalMTCreateHandler),
    (r"/cs/mt/update/approval", ApprovalMTUpdateHandler),
    (r"/cs/mtgroup/search", MTGroupSearchHandler),
    (r"/cs/mtgroup/all", MTGroupALLHandler),
    (r"/cs/mt/dealhistory/record", DealhistoryHandler),
    (r"/cs/mt/tradehistory/record", TradehistoryHandler),
    (r"/cs/mt/openposition/record", OpenpositionHandler),
    (r"/cs/mt/dealhistory/record/export", DealhistoryExportHandler),
    (r"/cs/mt/tradehistory/record/export", TradehistoryExportHandler),
    (r"/cs/mt/openposition/record/export", OpenpositionExportHandler),

    (r"/cs/fin/history", FinHistoryHandler),
    (r"/cs/fin/history/export", FinHistoryExportHandler),
    (r"/cs/fin/balance/ewallet", BalanceEwalletHandler),
]
