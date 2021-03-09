#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: manager.py
@time: 18/7/26 11:31
@description: 管理员操作
"""

import re

from base import *
from utils import utils
from utils.utils import format_date


# 新建内部用户
class InnerUserAddHandler(ApiHandler):
    def post(self):
        cname = self.get_json_argument('cname', default=None)
        email = self.get_json_argument('email', default=None)
        role_ids = self.get_json_argument('role_ids', default=None)
        password = self.get_json_argument('password', default=None)
        password_confirm = self.get_json_argument('password_confirm', default=None)
        firstname = self.get_json_argument('firstname', default=None)
        lastname = self.get_json_argument('lastname', default=None)
        mobile = self.get_json_argument('mobile', default=None)

        if not cname:
            self.error(u'请输入用户名称')
            return
        if not email:
            self.error(u'请输入电子邮箱')
            return
        if not role_ids:
            self.error(u'请输入用户角色')
            return
        if email.count('@') != 1 or email.count('.') == 0:
            self.error(u'邮箱格式不正确')
            return
        if not re.match('\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', email):
            self.error(u'邮箱格式不正确')
            return
        if (not password) or len(password) < 8:
            self.error(u'密码需要至少8位')
            return
        if password != password_confirm:
            self.error(u'两次密码不一致')
            return
        dbuser = self.userDao.select_by_login(None, email)
        if dbuser:
            self.error(u'邮箱或手机号错误')
            return

        statusa = "正常"
        _user = self.userDao.add(cname, firstname, lastname, mobile, email, utils.encrypt(password), "", statusa,
                                 role_ids)

        roles = self.roleDao.select_by_name("", -1)
        rolemap = {}
        for _role in roles:
            rolemap[_role.id] = _role.name
        roleids = ','.join(str(e) for e in _user.role_id)
        rolenames = ','.join(str(rolemap.get(e, "")) for e in _user.role_id)
        _mt = []
        self.success("create success",
                     {"cname": _user.cname, "firstname": _user.firstname, "lastname": _user.lastname,
                      "mobile": _user.mobile, "email": _user.email, "certid": _user.certid, "bank": _user.bank,
                      "bankbranch": _user.bankbranch, "swiftcode": _user.swiftcode, "agent_id": _user.agent_id,
                      "statusa": _user.statusa, "roleids": roleids, "rolenames": rolenames, "mt": _mt})
        return


# 搜索内部用户
class InnerUserSearchHandler(ApiHandler):
    def post(self):
        cname = self.get_json_argument('cname', default=None)
        role_ids = self.get_json_argument('role_ids', default=None)
        page = self.get_json_argument('page', default=None)

        roles = self.roleDao.select_by_name("", -1)
        rolemap = {}
        for _role in roles:
            rolemap[_role.id] = _role.name
        pagination = self.userDao.select_by_params_page(cname, role_ids, True, page)
        _objs = []
        for obj in pagination.items:
            rolelist = []
            for e in obj.role_id:
                rolelist.append({"role_id": str(e), "role_name": rolemap.get(e, "")})
            roleids = ','.join(str(e) for e in obj.role_id)
            rolenames = ','.join(str(rolemap.get(e, "")) for e in obj.role_id)
            _objs.append({"uid": obj.uid, "email": obj.email, "mobile": obj.mobile, "cname": obj.cname,
                          "roles": rolelist, "roleids": roleids, "rolenames": rolenames, "gid": obj.gid,
                          "createtime": format_date(obj.createtime)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 修改内部用户
class InnerUserUpdateHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)
        cname = self.get_json_argument('cname', default=None)
        email = self.get_json_argument('email', default=None)
        role_ids = self.get_json_argument('role_ids', default=None)
        password = self.get_json_argument('password', default=None)
        password_confirm = self.get_json_argument('password_confirm', default=None)

        if not uid:
            self.error(u'请输入用户ID')
            return
        if not cname:
            self.error(u'请输入用户名称')
            return
        if not email:
            self.error(u'请输入电子邮箱')
            return
        if not role_ids:
            self.error(u'请输入用户角色')
            return
        if email.count('@') != 1 or email.count('.') == 0:
            self.error(u'邮箱格式不正确')
            return
        if not re.match('\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', email):
            self.error(u'邮箱格式不正确')
            return
        dbuser = self.userDao.select_by_login(None, email)
        if dbuser and (dbuser.uid != uid):
            self.error(u'邮箱或手机号错误')
            return

        if password and password_confirm:
            if (not password) or len(password) < 8:
                self.error(u'密码需要至少8位')
                return
            if password != password_confirm:
                self.error(u'两次密码不一致')
                return
            self.userDao.update_info_passwd(uid, cname, email, utils.encrypt(password), role_ids)
            self.success("update success")
            return

        self.userDao.update_info(uid, cname, email, role_ids)
        self.success("update success")
        return


# 删除内部用户
class InnerUserDelHandler(ApiHandler):
    def post(self):
        uid = self.get_json_argument('uid', default=None)
        if not uid:
            self.error(u'请输入用户ID')
            return
        _fundflow = self.fundflowDao.select_by_uid(uid)
        if _fundflow:
            self.error(u'当前用户不可删除')
            return
        self.userDao.del_by_uid(uid)
        self.suc()
        return


# 导出内部用户
class InnerUserExportHandler(ApiHandler):
    def post(self):
        cname = self.get_argument('cname', default=None)
        role_ids = self.get_argument('role_ids', default=None)

        roles = self.roleDao.select_by_name("", -1)
        rolemap = {}
        for _role in roles:
            rolemap[_role.id] = _role.name
        items = self.userDao.select_by_params_page(cname, role_ids, True, -1)
        _titles = ["uid", "email", "mobile", "cname", "role_id", "gid", "createtime"]

        try:
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            self.write(','.join(_titles) + '\r\n')
            for obj in items:
                roles = ' '.join(str(rolemap.get(e, "")) for e in obj.role_id)
                self.write(','.join([str(obj.uid), str(obj.email), str(obj.mobile), str(obj.cname), roles,
                                     str(obj.gid), format_date(obj.createtime)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 角色管理
# 权限列表
class AccessListHandler(ApiHandler):
    def post(self):
        accessList = self.accessDao.select_all()
        _objs = []
        for obj in accessList:
            _objs.append({"id": obj.id, "name": obj.name, "url": obj.url, "element": obj.element,
                          "type": str(obj.type), "menu1": obj.menu1, "menu2": obj.menu2, "description": obj.description,
                          "createtime": format_date(obj.createtime)})
        self.suc(_objs)
        return


# 角色列表
class RoleSearchHandler(ApiHandler):
    def post(self):
        role_name = self.get_json_argument('role_name', default=None)
        page = self.get_json_argument('page', default=None)

        accessList = self.accessDao.select_all()
        accessmap = {}
        for _access in accessList:
            accessmap[_access.id] = _access.name
        pagination = self.roleDao.select_by_name(role_name, page)
        _objs = []
        for obj in pagination.items:
            accesslist = []
            accessids = ''
            accessnames = ''
            if obj.access:
                for e in obj.access:
                    accesslist.append({"access_id": str(e), "access_name": str(accessmap.get(e, ""))})
                accessids = ','.join(str(e) for e in obj.access)
                accessnames = ','.join(str(accessmap.get(e, "")) for e in obj.access)
            _objs.append({"id": obj.id, "name": obj.name, "access": obj.access, "builtin": obj.builtin,
                          "accesss": accesslist, "accessids": accessids, "accessnames": accessnames,
                          "description": obj.description, "createtime": format_date(obj.createtime)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 添加角色
class RoleAddHandler(ApiHandler):
    def post(self):
        role_name = self.get_json_argument('role_name', default=None)
        access_list = self.get_json_argument('access_list', default=None)
        description = self.get_json_argument('description', default=None)

        if not role_name:
            self.error(u'请输入角色名称')
            return
        if not access_list:
            self.error(u'请输入权限列表')
            return
        if not description:
            self.error(u'请输入角色说明')
            return
        rolebak = self.roleDao.select_by_name(role_name, 0)
        if rolebak:
            self.error(u'角色已经存在')
            return

        accessList = self.accessDao.select_all()
        accessmap = {}
        for _access in accessList:
            accessmap[_access.id] = _access.name
        _role = self.roleDao.add(role_name, access_list, True, description)
        accesslist = []
        accessids = ''
        accessnames = ''
        if _role.access:
            for e in _role.access:
                accesslist.append({"access_id": str(e), "access_name": str(accessmap.get(e, ""))})
            accessids = ','.join(str(e) for e in _role.access)
            accessnames = ','.join(str(accessmap.get(e, "")) for e in _role.access)
        self.success("create success",
                     {"id": _role.id, "name": _role.name, "access": accesslist, "accessids": accessids,
                      "accessnames": accessnames, "builtin": _role.builtin,
                      "description": _role.description, "createtime": format_date(_role.createtime)})
        return


# 修改角色
class RoleUpdateHandler(ApiHandler):
    def post(self):
        role_id = self.get_json_argument('role_id', default=None)
        role_name = self.get_json_argument('role_name', default=None)
        access_list = self.get_json_argument('access_list', default=None)
        description = self.get_json_argument('description', default=None)

        if not role_id:
            self.error(u'请输入角色ID')
            return
        if not role_name:
            self.error(u'请输入角色名称')
            return
        if not access_list:
            self.error(u'请输入权限列表')
            return

        accessList = self.accessDao.select_all()
        accessmap = {}
        for _access in accessList:
            accessmap[_access.id] = _access.name
        self.roleDao.update(role_id, role_name, access_list, description)
        _role = self.roleDao.select_by_id(role_id)
        accesslist = []
        accessids = ''
        accessnames = ''
        if _role.access:
            for e in _role.access:
                accesslist.append({"access_id": str(e), "access_name": str(accessmap.get(e, ""))})
            accessids = ','.join(str(e) for e in _role.access)
            accessnames = ','.join(str(accessmap.get(e, "")) for e in _role.access)
        self.success("update success",
                     {"id": _role.id, "name": _role.name, "access": accesslist, "accessids": accessids,
                      "accessnames": accessnames, "builtin": _role.builtin,
                      "description": _role.description, "createtime": format_date(_role.createtime)})
        return


# 删除角色
class RoleDelHandler(ApiHandler):
    def post(self):
        role_id = self.get_json_argument('role_id', default=None)
        if not role_id:
            self.error(u'请输入角色ID')
            return
        self.roleDao.del_by_id(role_id)
        self.success("delete success")
        return


# 导出角色
class RoleExportHandler(ApiHandler):
    def post(self):
        role_name = self.get_argument('role_name', default=None)

        accessList = self.accessDao.select_all()
        accessmap = {}
        for _access in accessList:
            accessmap[_access.id] = _access.name
        items = self.roleDao.select_by_name(role_name, -1)
        _titles = ["id", "name", "access", "builtin", "description", "createtime"]

        try:
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            self.write(','.join(_titles) + '\r\n')
            for obj in items:
                accessnames = ''
                if obj.access:
                    accessnames = ','.join(str(accessmap.get(e, "")) for e in obj.access)
                self.write(','.join([str(obj.id), str(obj.name), accessnames, str(obj.builtin),
                                     str(obj.description), format_date(obj.createtime)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# MT分组管理
# 查询MT分组类型
class MTGroupTypeHandler(ApiHandler):
    def get(self):
        grouptypeList = self.mtgrouptypeDao.select_all()
        _objs = []
        for obj in grouptypeList:
            _objs.append({"type": obj.type, "name": obj.name, "ename": obj.ename})
        self.suc(_objs)
        return


# 添加MT分组
class MTGroupCreateHandler(ApiHandler):
    def post(self):
        name = self.get_json_argument('name', default=None)
        mtname = self.get_json_argument('mtname', default=None)
        leverage = self.get_json_argument('leverage', default=None)
        spread = self.get_json_argument('spread', default=None)
        commission = self.get_json_argument('commission', default=None)
        maxbalance = self.get_json_argument('maxbalance', default=None)
        _type = self.get_json_argument('type', default=1)  # type 类型(1:标准组,2:专业组,3:VIP组,0:特殊组)

        if not name:
            self.error(u'请输入组名')
            return
        if not mtname:
            self.error(u'请输入MT账户名')
            return
        if not leverage:
            self.error(u'请输入杠杆率')
            return
        if (not spread) and spread != 0:
            self.error(u'请输入内佣加点')
            return
        if (not commission) and commission != 0:
            self.error(u'请输入外佣加点')
            return
        if not maxbalance:
            self.error(u'请输入资金上限')
            return

        try:
            _mtgroup = self.mtgroupDao.add(name, mtname, _type, spread, commission, leverage, maxbalance)
            logging.info("mtgroupDao add name=%s,mtname=%s,type=%s,spread=%s,commission=%s,leverage=%s,maxbalance=%s",
                         name, mtname, _type, spread, commission, leverage, maxbalance)
            self.success("create success",
                         {"name": _mtgroup.name, "mtname": _mtgroup.mtname, "type": _mtgroup.type,
                          "spread": _mtgroup.spread,
                          "commission": _mtgroup.commission, "maxbalance": "{:.6f}".format(_mtgroup.maxbalance),
                          "leverage": "{:.6f}".format(_mtgroup.leverage),
                          "createtime": format_date(_mtgroup.createtime)})
            return
        except Exception as ex:
            logging.error(ex)
            self.error("create fail")
            return


# 查询MT分组
class MTGroupSearchHandler(ApiHandler):
    def post(self):
        name = self.get_json_argument('name', default=None)
        page = self.get_json_argument('page', default=None)

        pagination = self.mtgroupDao.select_page(name, page)
        grouptypeList = self.mtgrouptypeDao.select_all()
        grouptypemap = {}
        for gt in grouptypeList:
            grouptypemap[gt.type] = gt.name
        grouptypemap2 = {}
        for gt in grouptypeList:
            grouptypemap2[gt.type] = gt.ename
        _objs = []
        for obj in pagination.items:
            maxb = ""
            if obj.maxbalance:
                maxb = "{:.6f}".format(obj.maxbalance)
            _objs.append({"name": obj.name, "mtname": obj.mtname, "type": obj.type, "typename": grouptypemap[obj.type],
                          "typeename": grouptypemap2[obj.type],
                          "commission": obj.commission, "maxbalance": maxb, "spread": obj.spread,
                          "leverage": "{:.6f}".format(obj.leverage), "createtime": format_date(obj.createtime)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 更新MT分组
class MTGroupUpdateHandler(ApiHandler):
    def post(self):
        name = self.get_json_argument('name', default=None)
        mtname = self.get_json_argument('mtname', default=None)
        _type = self.get_json_argument('type', default=None)
        leverage = self.get_json_argument('leverage', default=None)
        spread = self.get_json_argument('spread', default=None)
        commission = self.get_json_argument('commission', default=None)
        maxbalance = self.get_json_argument('maxbalance', default=None)

        if not name:
            self.error(u'请输入组名')
            return
        if not mtname:
            self.error(u'请输入MT账户名')
            return
        if not leverage:
            self.error(u'请输入杠杆率')
            return
        if (not spread) and spread != 0:
            self.error(u'请输入内佣加点')
            return
        if (not commission) and commission != 0:
            self.error(u'请输入外佣加点')
            return
        if not _type:
            self.error(u'请输入类型')
            return
        if not maxbalance:
            self.error(u'请输入资金上限')
            return

        _mtgroup = self.mtgroupDao.select_by_name(name)
        if not _mtgroup:
            self.error("组不存在")
            return
        self.mtgroupDao.update(name, mtname, _type, spread, commission, leverage, maxbalance)
        self.success("update success")
        return


# 删除MT分组
class MTGroupDelHandler(ApiHandler):
    def post(self):
        name = self.get_json_argument('name', default=None)
        self.mtgroupDao.del_by_name(name)
        self.success("delete success")
        return


# 导出MT分组
class MTGroupExportHandler(ApiHandler):
    def post(self):
        name = self.get_json_argument('name', default=None)

        items = self.mtgroupDao.select_page(name, -1)
        grouptypeList = self.mtgrouptypeDao.select_all()
        grouptypemap = {}
        for gt in grouptypeList:
            grouptypemap[gt.type] = gt.name
        grouptypemap2 = {}
        for gt in grouptypeList:
            grouptypemap2[gt.type] = gt.ename
        _titles = ["name", "mtname", "type", "typename", "typeename", "spread", "commission", "leverage", "maxbalance",
                   "createtime"]
        try:
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            self.write(','.join(_titles) + '\r\n')
            for obj in items:
                self.write(
                    ','.join(
                        [str(obj.name), str(obj.mtname), str(obj.type), grouptypemap[obj.type], grouptypemap2[obj.type],
                         str(obj.spread),
                         str(obj.commission), str(obj.leverage), str(obj.maxbalance),
                         format_date(obj.createtime)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 工作流管理
# 添加工作流
class WorkflowCreateHandler(ApiHandler):
    def post(self):
        name = self.get_json_argument('name', default=None)
        subject = self.get_json_argument('subject', default=None)
        body = self.get_json_argument('body', default=None)

        if not name:
            self.error(u'请输入类型名称')
            return
        if not subject:
            self.error(u'请输入标题')
            return
        if not body:
            self.error(u'请输入内容文本')
            return

        _task = self.taskDao.add(name, "", "", "", subject, body)
        self.success("create success",
                     {"type": _task.type, "name": _task.name, "trigger": _task.trigger, "success": _task.success,
                      "fail": _task.fail, "subject": _task.subject, "body": _task.body,
                      "createtime": format_date(_task.createtime)})
        return


# 查询工作流
class WorkflowSearchHandler(ApiHandler):
    def post(self):
        _type = self.get_json_argument('type', default=None)
        subject = self.get_json_argument('subject', default=None)
        page = self.get_json_argument('page', default=None)

        pagination = self.taskDao.search_page(_type, subject, page)
        _objs = []
        for obj in pagination.items:
            _objs.append({"type": obj.type, "name": obj.name, "trigger": obj.trigger, "success": obj.success,
                          "fail": obj.fail, "subject": obj.subject, "body": obj.body,
                          "createtime": format_date(obj.createtime)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 查询工作流类型
class WorkflowTypeHandler(ApiHandler):
    def get(self):
        items = self.taskDao.search_page(None, None, -1)
        _objs = []
        for obj in items:
            _objs.append({"type": obj.type, "name": obj.name})
        self.suc(_objs)
        return


# 更新工作流
class WorkflowUpdateHandler(ApiHandler):
    def post(self):
        _type = self.get_json_argument('type', default=None)
        name = self.get_json_argument('name', default=None)
        subject = self.get_json_argument('subject', default=None)
        body = self.get_json_argument('body', default=None)

        if not _type:
            self.error(u'请输入类型ID')
            return
        if not name:
            self.error(u'请输入类型名称')
            return
        if not subject:
            self.error(u'请输入标题')
            return
        if not body:
            self.error(u'请输入内容文本')
            return

        self.taskDao.update(_type, name, subject, body)
        self.success("update success")
        return


# 删除工作流
class WorkflowDelHandler(ApiHandler):
    def post(self):
        _type = self.get_json_argument('type', default=None)
        if not _type:
            self.error(u'请输入类型ID')
            return

        self.taskDao.del_by_type(_type)
        self.success("delete success")
        return


# 导出工作流
class WorkflowExportHandler(ApiHandler):
    def post(self):
        _type = self.get_argument('type', default=None)
        subject = self.get_argument('subject', default=None)

        items = self.taskDao.search_page(_type, subject, -1)
        _titles = ["type", "name", "trigger", "success", "fail", "subject", "body", "createtime"]

        try:
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            self.write(','.join(_titles) + '\r\n')
            for obj in items:
                self.write(','.join([str(obj.type), str(obj.name), str(obj.trigger), str(obj.success), str(obj.fail),
                                     str(obj.subject), str(obj.body), format_date(obj.createtime)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 添加工作流节点
class WorkflowNodeCreateHandler(ApiHandler):
    def post(self):
        previous = self.get_json_argument('previous', default=None)
        name = self.get_json_argument('name', default=None)
        t_type = self.get_json_argument('t_type', default=None)
        approve = self.get_json_argument('approve', default=None)
        step = self.get_json_argument('step', default=None)
        canapprove = self.get_json_argument('canapprove', default=None)
        canreturn = self.get_json_argument('canreturn', default=None)
        canreject = self.get_json_argument('canreject', default=None)
        returned = self.get_json_argument('returned', default=None)
        role_id = self.get_json_argument('role_id', default=None)

        # if not previous:
        #     self.error(u'请输入上一个节点ID')
        #     return
        if not name:
            self.error(u'请输入节点名称')
            return
        if not t_type:
            self.error(u'请输入工作流ID')
            return
        # if not approve:
        #    self.error(u'请输入approve命名')
        #    return
        # if not returned:
        #    self.error(u'请输入被return命名')
        #    return
        if not role_id:
            self.error(u'请输入处理者role')
            return
        _role = self.roleDao.select_by_id(role_id)
        if not _role:
            self.error(u'角色不存在')
            return

        _tasknode = self.tasknodeDao.add(previous, name, t_type, approve, returned, step, canapprove, canreturn,
                                         canreject, role_id)
        self.success("create success",
                     {"id": _tasknode.id, "previous": _tasknode.previous, "name": _tasknode.name,
                      "t_type": _tasknode.t_type, "approve": _tasknode.approve,
                      "returned": _tasknode.returned, "step": _tasknode.step, "canapprove": _tasknode.canapprove,
                      "canreturn": _tasknode.canreturn, "canreject": _tasknode.canreject, "role_id": _tasknode.role_id,
                      "createtime": format_date(_tasknode.createtime)})
        return


# 查询工作流节点
class WorkflowNodeSearchHandler(ApiHandler):
    def post(self):
        _type = self.get_json_argument('type', default=None)
        page = self.get_json_argument('page', default=None)
        if not _type:
            self.error(u'请输入类型ID')
            return

        roleList = self.roleDao.select_all()
        rolemap = {}
        for _role in roleList:
            rolemap[_role.id] = _role.name
        pagination = self.tasknodeDao.search_page(_type, page)
        _objs = []
        for obj in pagination.items:
            rolename = rolemap[obj.role_id]
            _objs.append({"id": obj.id, "previous": obj.previous, "name": obj.name, "t_type": obj.t_type,
                          "approve": obj.approve, "returned": obj.returned, "step": obj.step,
                          "canapprove": obj.canapprove, "canreturn": obj.canreturn,
                          "canreject": obj.canreject, "role_id": obj.role_id, "rolename": rolename,
                          "createtime": format_date(obj.createtime)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 更新工作流节点
class WorkflowNodeUpdateHandler(ApiHandler):
    def post(self):
        _id = self.get_json_argument('id', default=None)
        name = self.get_json_argument('name', default=None)
        t_type = self.get_json_argument('t_type', default=None)
        approve = self.get_json_argument('approve', default=None)
        canapprove = self.get_json_argument('canapprove', default=None)
        canreturn = self.get_json_argument('canreturn', default=None)
        canreject = self.get_json_argument('canreject', default=None)
        returned = self.get_json_argument('returned', default=None)
        role_id = self.get_json_argument('role_id', default=None)

        if not t_type:
            self.error(u'请输入工作流ID')
            return
        if not name:
            self.error(u'请输入节点名称')
            return
        """"
        if not approve:
            self.error(u'请输入approve命名')
            return
        if not returned:
            self.error(u'请输入被return命名')
            return
        """
        if not role_id:
            self.error(u'请输入处理者role')
            return
        self.tasknodeDao.update(_id, name, t_type, approve, returned, canapprove, canreturn, canreject, role_id)
        self.success("update success")
        return


# 删除工作流节点
class WorkflowNodeDelHandler(ApiHandler):
    def post(self):
        _id = self.get_json_argument('id', default=None)
        if not _id:
            self.error(u'请输入类型ID')
            return
        try:
            self.tasknodeDao.del_by_id(_id)
            self.success(u'操作成功')
            return
        except Exception as ex:
            logging.error(ex)
            self.error(u'操作失败')
            return


# 导出工作流节点
class WorkflowNodeExportHandler(ApiHandler):
    def get(self):
        _type = self.get_json_argument('type', default=None)
        if not _type:
            self.error(u'请输入类型ID')
            return

        items = self.tasknodeDao.search_page(_type, -1)
        _titles = ["id", "previous", "name", "t_type", "approve", "returned", "step", "canapprove", "canreturn",
                   "canreject", "role_id", "createtime"]
        try:
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            self.write(','.join(_titles) + '\r\n')
            for obj in items:
                self.write(','.join([str(obj.id), str(obj.previous), str(obj.name), str(obj.t_type), str(obj.approve),
                                     str(obj.returned), str(obj.step), str(obj.canapprove), str(obj.canreturn),
                                     str(obj.canreject), str(obj.role_id), format_date(obj.createtime)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 管理员用的搜索所有已完成未完成任务的接口
class WorkflowTaskHandler(ApiHandler):
    def post(self):
        page = self.get_json_argument('page', default=None)
        self.success("")
        return


# 系统参数配置管理
class SysconfViewHandler(ApiHandler):
    def get(self):
        items = self.configDao.select_all()
        _objs = []
        for obj in items:
            _objs.append({"name": obj.name, "value": obj.value, "comment": obj.comment})
        self.suc(_objs)
        return


class SysconfAddHandler(ApiHandler):
    def post(self):
        name = self.get_json_argument('name', default=None)
        value = self.get_json_argument('value', default=None)
        comment = self.get_json_argument('comment', default=None)
        if not name:
            self.error(u'请输入参数项名称')
            return
        if not value:
            self.error(u'请输入参数值')
            return
        _tconfig = self.tconfigDao.select_by_name(name)
        if _tconfig:
            self.error(u'参数项已经存在')
            return
        _tconfig = self.tconfigDao.add(name, value, comment)
        self.success("create success", {"name": _tconfig.name, "value": _tconfig.value, "comment": _tconfig.comment})
        return


class SysconfUpdateHandler(ApiHandler):
    def post(self):
        name = self.get_json_argument('name', default=None)
        value = self.get_json_argument('value', default=None)
        comment = self.get_json_argument('comment', default=None)
        if not name:
            self.error(u'请输入参数项名称')
            return
        if not value:
            self.error(u'请输入参数值')
            return
        _tconfig = self.tconfigDao.select_by_name(name)
        if not _tconfig:
            self.error(u'参数项不存在')
            return
        self.tconfigDao.update_value(name, value, comment)
        self.success("update success")
        return


# 待处理的任务
class UnfinishTaskSearchHandler(ApiHandler):
    def post(self):
        task_type = self.get_json_argument('task_type', default=None)
        o_cname = self.get_json_argument('o_cname', default=None)
        page = self.get_json_argument('page', default=None)

        pagination = self.vtaskitemDao.select_page(task_type, None, -1, o_cname, False, page)
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


# 已完成的任务
class FinishTaskSearchHandler(ApiHandler):
    def post(self):
        task_type = self.get_json_argument('task_type', default=None)
        o_cname = self.get_json_argument('o_cname', default=None)
        page = self.get_json_argument('page', default=None)

        # task_type, o_uid, state, o_cname, role_ids, page
        pagination = self.vtaskitemDao.select_page(task_type, None, -2, o_cname, False, page)
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


handlers = [
    (r"/ma/inner/user/add", InnerUserAddHandler),
    (r"/ma/inner/user/search", InnerUserSearchHandler),
    (r"/ma/inner/user/update", InnerUserUpdateHandler),
    (r"/ma/inner/user/del", InnerUserDelHandler),
    (r"/ma/inner/user/export", InnerUserExportHandler),

    (r"/ma/access/list", AccessListHandler),
    (r"/ma/role/search", RoleSearchHandler),
    (r"/ma/role/add", RoleAddHandler),
    (r"/ma/role/update", RoleUpdateHandler),
    (r"/ma/role/del", RoleDelHandler),
    (r"/ma/role/export", RoleExportHandler),

    (r"/ma/mtgroup/type", MTGroupTypeHandler),
    (r"/ma/mtgroup/search", MTGroupSearchHandler),
    (r"/ma/mtgroup/add", MTGroupCreateHandler),
    (r"/ma/mtgroup/update", MTGroupUpdateHandler),
    (r"/ma/mtgroup/del", MTGroupDelHandler),
    (r"/ma/mtgroup/export", MTGroupExportHandler),

    (r"/ma/workflow/type", WorkflowTypeHandler),
    (r"/ma/workflow/search", WorkflowSearchHandler),
    (r"/ma/workflow/add", WorkflowCreateHandler),
    (r"/ma/workflow/update", WorkflowUpdateHandler),
    (r"/ma/workflow/del", WorkflowDelHandler),
    (r"/ma/workflow/export", WorkflowExportHandler),

    (r"/ma/workflow/node/search", WorkflowNodeSearchHandler),
    (r"/ma/workflow/node/add", WorkflowNodeCreateHandler),
    (r"/ma/workflow/node/update", WorkflowNodeUpdateHandler),
    (r"/ma/workflow/node/del", WorkflowNodeDelHandler),
    (r"/ma/workflow/node/export", WorkflowNodeExportHandler),

    (r"/ma/workflow/task", WorkflowTaskHandler),

    (r"/ma/sysconf/view", SysconfViewHandler),
    (r"/ma/sysconf/add", SysconfAddHandler),
    (r"/ma/sysconf/update", SysconfUpdateHandler),

    (r"/ma/task/search/unfinish", UnfinishTaskSearchHandler),
    (r"/ma/task/search/finish", FinishTaskSearchHandler),
]
