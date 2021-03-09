#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: base.py
@time: 18/6/15 15:11
@description: 路由层
"""

import binascii
import hashlib
import json
import logging
import os

import jinja2
import time
import tornado.escape
import tornado.web

from model import access, role, task, tasknode
from model import config
from model import fundflow, extpay, tconfig
from model import messageitem, internalgroup
from model import models
from model import taskitem, taskhistory, message
from model import user, mtgroup, agent, views, mt
from utils import redisToSession
from utils import utils

logger = logging.getLogger('xwcrm.handler')

__ALL__ = ['HTTPError', 'BaseHandler', 'logger', ]


class BaseHandler(tornado.web.RequestHandler):
    '''
    第二级Handler
    '''

    def data_received(self, chunk):
        pass

    # 类的静态变量用于保存登录信息, 存储的是token对应的user_id
    __TOKEN_LIST = {}

    def __init__(self, application, request, **kwargs):
        self.db_session = models.Session()
        self.picDao = user.PicDao()
        self.userDao = user.UserDao()
        self.picDao = user.PicDao()
        self.agentDao = agent.TAgentDao()
        self.fundflowDao = fundflow.TFundflowDao()
        self.extpayDao = extpay.TExtpayDao()
        self.configDao = tconfig.TConfigQuery()
        self.tconfigDao = tconfig.TConfigDao()
        self.accessDao = access.TAccessDao()
        self.roleDao = role.TRoleDao()
        self.taskDao = task.TTaskDao()
        self.tasknodeDao = tasknode.TTaskNodeDao()
        self.taskitemDao = taskitem.TTaskItemDao()
        self.taskhistoryDao = taskhistory.TTaskHistoryDao()
        self.messageDao = message.TMessageDao()
        self.messageitemDao = messageitem.TMessageItemDao()
        self.internalgroupDao = internalgroup.TInternalGroupDao()
        self.mtgroupDao = mtgroup.TMTGroupDao()
        self.mtgrouptypeDao = mtgroup.TMTGrouptypeDao()
        self.fundflowDao = fundflow.TFundflowDao()
        self.fundtypeDao = fundflow.TFundtypeDao()
        self.vmtuserDao = views.VMtuserDao()
        self.vdealclosedDao = views.VDealclosedDao()
        self.vfxusdcnhDao = views.VFxusdcnhDao()
        self.vcommissionDao = views.VCommissionDao()
        self.vtaskitemDao = views.VTaskitemDao()
        self.vclientDao = views.VClientDao()
        self.vdealhistoryDao = views.VDealhistoryDao()
        self.vtradehistoryDao = views.VTradehistoryDao()
        self.vopenpositionDao = views.VOpenpositionDao()
        self.mtDao = mt.MTDao()
        self.sredis = redisToSession.Sredis()
        self.taskSuccess = task.TaskSuccess()
        self.taskFail = task.TaskFail()
        super(BaseHandler, self).__init__(application, request, **kwargs)

    def on_finish(self):
        '''
        关闭postgre连接
        :return:
        '''
        self.db_session.close()

    def get_json_argument(self, name, default=None):
        '''
        获取前端传过来的参数
        :param name: 参数名
        :param default: 参数值
        :return: 参数值
        '''
        jsonbody = unicode(self.request.body, errors='ignore')
        args = tornado.escape.json_decode(jsonbody)
        # logger.info(args)
        name = tornado.escape.to_unicode(name)
        if name in args:
            return args[name]
        else:
            return default

    def new_token(self):
        '''
        生成新token
        :return:
        '''
        while True:
            new_token = binascii.hexlify(os.urandom(16)).decode("utf8")
            if new_token not in self.__TOKEN_LIST:
                return new_token

    @property
    def db(self):
        return self.application.db

    def render_string(self, template_name, **kwargs):
        try:
            template = self.application.jinja_env.get_template(template_name)
        except jinja2.TemplateNotFound as e:
            logger.error(e)
            raise

        namespace = dict(
            static_url=self.static_url,
            xsrf_token=self.xsrf_token,

            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url
        )
        namespace.update(kwargs)

        return template.render(namespace)

    @property
    def ip(self):
        return self.request.remote_ip

    @property
    def ip2int(self):
        return utils.ip2int(self.request.remote_ip)

    def on_login_success(self, user_id, utype):
        self.set_cookie('_token', user_id, expires_days=config.cookie_days)
        self.set_cookie('_tp', utype, expires_days=config.cookie_days)

    def get_current_user(self):
        '''
        获取当前登陆的用户
        :return:
        '''
        # 从cookie中读取token
        token = self.get_cookie('_token')
        utype = self.get_cookie('_tp')
        if token is None or utype is None:
            return None

        user_id = token
        # 没有找到就返回none, 表示该用户没有登录
        return self.userDao.select_by_uid(user_id)


# 基础类
class APIBaseHandler(tornado.web.RequestHandler):
    '''
    没用
    '''

    def data_received(self, chunk):
        pass

    def db_find_one(self, coll, param):
        return self.application.db[coll].find_one(param)

    def db_update(self, coll, param, data, upsert=False):
        return self.application.db[coll].update(param, {"$set": data}, upsert)


# RESTful API接口实现类
class ApiHandler(BaseHandler):
    '''
    第三级handler
    '''

    @tornado.gen.coroutine
    def prepare(self):
        exclude_url_log = ["/cs/customer/update", "/profile/upload/?(?P<file_type>[A-Za-z0-9-]+)?",
                           "/profile/upload/idcard", "/profile/upload/idcardback","/profile/upload/bankcard"]
        if (self.request.uri in exclude_url_log) or (self.request.path in exclude_url_log):
            pass
        else:
            logger.info('>>> method=%s, url=%s, parameter=%s', self.request.method, self.request.uri, self.request.body)
        public_url = ["/", "/register", "/register/code", "/resetpwd/code", "/register/verify",
                      "/resetpwd", "/logout", "/login", "/pay/lizhi/callback", "/profile/view",
                      "/bg/login"]
        if (self.request.uri in public_url) or (self.request.path in public_url):
            return
        try:
            headers = self.request.headers
            try:
                token = headers['Auth-Token']
                if not token:
                    self.current_user = None
                    self.err(901, "token error")
                    return
            except Exception as e:
                self.current_user = None
                self.err(901, "token error")
                return
            logger.info('token=%s', token)
            _user = self.get_current(token)
            if not _user:
                self.err(901, "un login")
                return
            self.current_user = _user
        except Exception as ex:
            logging.error(ex)
            self.current_user = None
            self.err(901, "un login")
            return

    # 预处理header，允许跨域
    """
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
    """

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def get_current(self, token):
        '''
        已知token，获取当前登陆用户
        :param token: 标识码
        :return: 当前登陆用户
        '''
        redis_value = self.sredis.__getitem__(token)
        if not redis_value:
            return None
        datajson = json.loads(redis_value)
        uid = datajson['uid']
        utype = datajson['utype']
        if uid is None or utype is None:
            return None
        current_user = self.userDao.select_by_uid(uid)
        return current_user

    def update_access_token(self, user_id, user_name, utype=''):
        '''
        更新标识码
        :param user_id: 用户id
        :param user_name: 用户名
        :param utype: 用户类型
        :return: 新标识码
        '''
        secret_key = "XWCRMxwcrm"
        access_create = int(time.time())

        # 使用下面四个参数生成 new_token
        tmpArr = [secret_key, user_id, utype, str(access_create)]
        tmpArr.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, tmpArr)
        new_token = sha1.hexdigest()

        # 向客户端返回 new_token
        self.set_header("Auth-Token", new_token)
        self.set_header("Auth-Username", user_name)
        # 将新token更新到redis
        self.sredis.__setitem__(new_token, json.dumps({"uid": user_id, "utype": utype}))
        return new_token

    def del_access_token(self, token):
        '''
        清除标识码
        :param token:标识码
        :return: null
        '''
        self.set_header("Auth-Token", "")
        self.set_header("Auth-Username", "")
        self.sredis.__delitem__(token)

    def _finish(self, chunk=None, info=""):
        if chunk:
            response = {"meta": {"code": 200, "info": info}, "data": chunk}
        else:
            if info is "":
                response = {"meta": {"code": 404, "info": "not found"}, "data": {}}
            else:
                response = {"meta": {"code": 403, "info": info}, "data": {}}

        callback = tornado.escape.to_basestring(self.get_argument("callback", None))
        # 兼容jsonp请求
        if callback:
            # 直接发送js代码段发起执行
            # self.set_header("Content-Type", "application/x-javascript")
            # 发送数据文本，需要前端再处理
            self.set_header("Content-Type", "text/html")
            response = "%s(%s)" % (callback, tornado.escape.json_encode(response))
        else:
            # 直接发送json
            # self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.set_header("Content-Type", "text/html")
        super(ApiHandler, self).finish(response)

    def suc(self, param=None):
        '''
        请求成功（无提示信息）
        :param param:数据
        :return: null
        '''
        self.db_session.close()
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        super(ApiHandler, self).finish({"code": 200, "msg": "", "data": param})

    def success(self, msg="", param=None):
        '''
        请求成功（有提示信息）
        :param msg: 提示信息
        :param param: 数据
        :return: null
        '''
        self.db_session.close()
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        super(ApiHandler, self).finish({"code": 200, "msg": msg, "data": param})

    def err(self, code, msg="", param=None):
        '''
        请求失败（自定义code）
        :param code: 响应码
        :param msg: 提示信息
        :param param: 数据
        :return: null
        '''
        self.db_session.close()
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        logger.error(">>> code=%s,msg=%s,data=%s", code, msg, param)
        super(ApiHandler, self).finish({"code": code, "msg": msg, "data": param})

    def error(self, msg="", param=None):
        '''
        请求失败（code固定900）
        :param msg: 提示信息
        :param param: 数据
        :return: null
        '''
        self.db_session.close()
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        logger.error(">>> code=900,msg=%s,data=%s", msg, param)
        super(ApiHandler, self).finish({"code": 900, "msg": msg, "data": param})


# 请求权限处理类
class AccessHandler(ApiHandler):
    '''
    第四级handler
    '''

    def prepare(self):
        '''
        检查权限
        '''
        # 获取请求头，并对请求头做做处理
        headers = self.request.headers
        if not self.ckeck_access_token(headers):
            # 不通过则返回禁止信息
            self._finish(chunk=None, info="access forbidden")
        else:
            return

    def ckeck_access_token(self, headers):
        # 判断host是否合法
        logging.info('Host:' + headers["Host"])
        # 判断token
        if ("Access-Type" and "Access-Token" and "Access-Account") in headers:
            access_type = headers["Access-Type"]
            access_token = headers["Access-Token"]
            access_account = headers["Access-Account"]

            logging.info(access_token)
            # 自定义字段 access_type
            if access_type == "__YOUR_TYPE__":
                # 查询数据库
                cont = self.db_find_one("user", {"account": access_account})
            else:
                return False

            if cont["access_token"] == access_token:
                # token有效期7200秒
                # 其中，在过期前10分钟有获取新token资格
                # 一旦获得新token，旧token立即废弃
                if int(time.time()) <= int(cont["access_create"]) + 7200:
                    # 如果token合法且即将过期，则更新
                    if int(time.time()) > int(cont["access_create"]) + 6600:
                        # 生成新的token
                        self.update_access_token(access_account, access_type)
                    return True
        # 执行到最后还不返回True就说明token错误
        return False
