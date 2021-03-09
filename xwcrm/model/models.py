#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: models.py
@time: 18/6/20 17:33
"""

from __future__ import with_statement, absolute_import

import logging

from sqlalchemy import *
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import func

from model import config
from .cache import cached_property

BaseModel = declarative_base()
metadata = BaseModel.metadata
db = create_engine(config.db_conf, echo=True, poolclass=NullPool)
Session = sessionmaker(bind=db)

logger = logging.getLogger('xwcrm.basedb')


def tostr(s):
    if isinstance(s, bytearray):
        return str(s)
    return s


class Pagination(object):
    """
    分页
    """

    def __init__(self, query, page, per_page=20):
        """
        初始化对象
        :param query:查询结果
        :param page: 当前页
        :param per_page: 每页显示条数
        """
        self.query = query
        self.per_page = per_page
        max_page = max(0, self.total - 1) // per_page + 1  # "/"就表示浮点数除法，返回浮点结果;"//"表示整数除法。
        _page = int(page)
        self.page = max_page if _page > max_page else _page

    @cached_property
    def total(self):
        """
        查询结果总个数
        :return:
        """
        return self.query.count()

    @cached_property
    def items(self):
        # offset:开始位置  limit：限制个数
        list = self.query.offset((self.page - 1) * self.per_page).limit(self.per_page).all()
        if not list:
            return []
        return list

    def iter_pages(self, left_edge=1, left_current=1,
                   right_current=2, right_edge=1):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or (
                    num > self.page - left_current - 1 and num < self.page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    @cached_property
    def has_prev(self):
        return self.page > 1

    @cached_property
    def prev_num(self):
        return self.page - 1

    @cached_property
    def has_next(self):
        return self.page < self.pages  # self.pages == max_page

    @cached_property
    def next_num(self):
        return self.page + 1

    @cached_property
    def pages(self):
        return max(0, self.total - 1) // self.per_page + 1


class DBDao:
    """
    数据库操作基类
    """

    def __init__(self):
        self.session = Session()

    def _add(self, obj):
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        self.session.close()
        return obj


class BaseDB(BaseModel):
    """
    内部功能未使用
    """
    __abstract__ = True
    """
    BaseDB

    dbcur should be overwirte
    """
    placeholder = '%s'

    @staticmethod
    def escape(string):
        return '`%s`' % string

    @property
    def dbcur(self):
        if self.conn.unread_result:
            try:
                self.conn.get_rows()
            except Exception as e:
                logging.error(e)
                pass
        self.conn.ping(reconnect=True)
        return self.conn.cursor()

    def _execute(self, sql_query, values=[]):
        dbcur = self.dbcur
        dbcur.execute(sql_query, values)
        return dbcur

    def _select(self, tablename=None, what="*", where="", where_values=[], offset=0, limit=None):
        tablename = self.escape(tablename or self.__tablename__)
        if isinstance(what, list) or isinstance(what, tuple) or what is None:
            what = ','.join(self.escape(f) for f in what) if what else '*'

        sql_query = "SELECT %s FROM %s" % (what, tablename)
        if where: sql_query += " WHERE %s" % where
        if limit: sql_query += " LIMIT %d, %d" % (offset, limit)
        logger.debug("<sql: %s>", sql_query)

        for row in self._execute(sql_query, where_values):
            yield [tostr(x) for x in row]

    def _select2dic(self, tablename=None, what="*", where="", where_values=[], offset=0, limit=None):
        tablename = self.escape(tablename or self.__tablename__)
        if isinstance(what, list) or isinstance(what, tuple) or what is None:
            what = ','.join(self.escape(f) for f in what) if what else '*'

        sql_query = "SELECT %s FROM %s" % (what, tablename)
        if where: sql_query += " WHERE %s" % where
        if limit: sql_query += " LIMIT %d, %d" % (offset, limit)
        logger.debug("<sql: %s>", sql_query)

        dbcur = self._execute(sql_query, where_values)
        fields = [f[0] for f in dbcur.description]

        for row in dbcur:
            yield dict(zip(fields, [tostr(x) for x in row]))

    def _replace(self, tablename=None, **values):
        tablename = self.escape(tablename or self.__tablename__)
        if values:
            _keys = ", ".join(self.escape(k) for k in values.iterkeys())
            _values = ", ".join([self.placeholder, ] * len(values))
            sql_query = "REPLACE INTO %s (%s) VALUES (%s)" % (tablename, _keys, _values)
        else:
            sql_query = "REPLACE INTO %s DEFAULT VALUES" % tablename
        logger.debug("<sql: %s>", sql_query)

        if values:
            dbcur = self._execute(sql_query, values.values())
        else:
            dbcur = self._execute(sql_query)
        return dbcur.lastrowid

    def _insert(self, tablename=None, **values):
        tablename = self.escape(tablename or self.__tablename__)
        if values:
            _keys = ", ".join((self.escape(k) for k in values.iterkeys()))
            _values = ", ".join([self.placeholder, ] * len(values))
            sql_query = "INSERT INTO %s (%s) VALUES (%s)" % (tablename, _keys, _values)
        else:
            sql_query = "INSERT INTO %s DEFAULT VALUES" % tablename
        logger.debug("<sql: %s>", sql_query)

        if values:
            dbcur = self._execute(sql_query, values.values())
        else:
            dbcur = self._execute(sql_query)
        return dbcur.lastrowid

    def _update(self, tablename=None, where="1=0", where_values=[], **values):
        tablename = self.escape(tablename or self.__tablename__)
        _key_values = ", ".join(["%s = %s" % (self.escape(k), self.placeholder) for k in values.iterkeys()])
        sql_query = "UPDATE %s SET %s WHERE %s" % (tablename, _key_values, where)
        logger.debug("<sql: %s>", sql_query)

        return self._execute(sql_query, values.values() + list(where_values))

    def _delete(self, tablename=None, where="1=0", where_values=[]):
        tablename = self.escape(tablename or self.__tablename__)
        sql_query = "DELETE FROM %s" % tablename
        if where: sql_query += " WHERE %s" % where
        logger.debug("<sql: %s>", sql_query)

        return self._execute(sql_query, where_values)

    def to_dict(self):
        column_name_list = [
            value[0] for value in self._sa_instance_state.attrs.items()
        ]
        return dict(
            (column_name, getattr(self, column_name, None)) \
            for column_name in column_name_list
        )


class TUser(BaseDB):
    """
    类TUser ORM 表t_user（用户）
    """
    __tablename__ = 't_user'

    uid = Column('uid', CHAR(32), primary_key=True, nullable=False,
                 server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # 用户表: 用户id
    email = Column('email', String(64), nullable=False)  # 电子邮箱
    mobile = Column('mobile', String(32), nullable=True)  # 手机号
    passwd = Column('passwd', String(256), nullable=False)  # 密码(SHA512密文)
    emailv = Column('emailv', Boolean, default=False, nullable=False)  # 电子邮箱是否验证
    mobilev = Column('mobilev', Boolean, default=False, nullable=True)  # 手机号是否验证
    agent_id = Column('agent_id', CHAR(8), nullable=True)  # 上级代理ID
    # 用户状态A(界面显示的用户状态: 正常,交易冻结,出金冻结,入金冻结,警告,封禁,删除,审核中)ID
    statusa = Column('statusa', String(128), nullable=True)
    statusb = Column('statusb', String(128), nullable=True)  # 用户状态B
    cname = Column('cname', String(64), nullable=True)  # 中文姓名(界面上姓名)
    firstname = Column('firstname', String(64), nullable=True)  # 英文名
    middlename = Column('middlename', String(64), nullable=True)  # 中间名
    lastname = Column('lastname', String(64), nullable=True)  # 英文姓
    cert = Column('cert', String(16), nullable=True)  # 有效证件
    certid = Column('certid', String(128), nullable=True)  # 证件号
    bankaccount = Column('bankaccount', String(32), nullable=True)  # 银行账户
    bank = Column('bank', String(128), nullable=True)  # 开户行
    bankbranch = Column('bankbranch', String(128), nullable=True)  # 支行名称
    swiftcode = Column('swiftcode', String(16), nullable=True)  # SWIFT CODE
    mtlogin = Column('mtlogin', ARRAY(String), nullable=True)  # MT账户 元素最多3个
    gid = Column('gid', CHAR(32), nullable=True)  # 用户分组
    role_id = Column('role_id', ARRAY(String), nullable=True)  # 用户角色
    report = Column('report', CHAR(64), nullable=True)  # 用户经理
    country = Column('country', String(128), nullable=True)  # 国家
    state = Column('state', String(128), nullable=True)  # 州省
    address = Column('address', String(1024), nullable=True)  # 地址
    certpic0 = Column('certpic0', String(32), nullable=True)  # 证件图片0
    certpic1 = Column('certpic1', String(32), nullable=True)  # 证件图片1
    bankpic0 = Column('bankpic0', String(32), nullable=True)  # 银行卡图片0
    addrpic0 = Column('addrpic0', String(32), nullable=True)  # 地址图⽚0
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, cname, firstname, lastname, mobile, email, passwd, agent_id, statusa, role_id, mtlogin, mobilev,
                 emailv):
        self.cname = cname
        self.mobile = mobile
        if mobile:
            self.mobilev = True
        self.email = email
        if email:
            self.emailv = True
        self.passwd = passwd
        self.agent_id = agent_id
        self.statusa = statusa
        self.statusb = ""
        self.role_id = role_id
        self.mtlogin = mtlogin
        self.firstname = firstname
        self.lastname = lastname
        self.mobilev = mobilev
        self.emailv = emailv


class TPic(BaseDB):
    """
    类TPic ORM 表t_pic（图片存放）
    """
    __tablename__ = 't_pic'

    id = Column('id', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # 图片存放表: 图片序号id
    uid = Column('uid', CHAR(32), nullable=False)  # 用户id
    pic = Column('pic', LargeBinary, nullable=True)  # 图片流
    ocrcode = Column('ocrcode', CHAR(32), nullable=False)  # OCR识别码
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间

    def __init__(self, uid, pic, ocrcode):
        self.uid = uid
        self.pic = pic
        self.ocrcode = ocrcode


class TAgent(BaseDB):
    """
    类TAgent ORM 表t_agent（代理商）
    """
    __tablename__ = 't_agent'

    agentid = Column('agentid', CHAR(8), primary_key=True, nullable=False)  # 代理商表: 代理商id
    uid = Column('uid', CHAR(32), nullable=False)  # 用户id
    parentid = Column('parentid', CHAR(8), nullable=True)  # 上级代理
    level = Column('level', Integer, nullable=False)  # 代理商层级level:[1,3]
    reward = Column('reward', Integer, nullable=False)  # 代理返佣
    status = Column('status', String(128), nullable=False)  # 代理商状态(正常,返佣暂停)
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, agentid, uid, level, reward, status, parentid=None):
        self.agentid = agentid
        self.uid = uid
        self.parentid = parentid
        self.level = level
        self.reward = reward
        self.status = status


class TFundflow(BaseDB):
    """
    类TFundflow ORM 表t_fundflow（客户资金变动）
    """
    __tablename__ = 't_fundflow'

    id = Column('id', BigInteger, primary_key=True, autoincrement=True, nullable=False)  # 客户资金变动表: 单号
    uid = Column('uid', CHAR(32), nullable=False)  # 客户id
    # 类型(10=⽹银⼊⾦,11=电汇入金,19=⽹银⼊⾦失败,20=MT出⾦,21=会计出⾦,30=MT内转,31=电⼦钱包内转,50=佣⾦结算N,51=佣⾦结算W,99=MT操作失败)
    type = Column('type', Integer, nullable=False)
    mtlogin = Column('mtlogin', String(10), nullable=True)  # MT账户
    transaction = Column('transaction', String(21), nullable=True)  # 交易号
    credit = Column('credit', DECIMAL, nullable=True)  # 借
    debit = Column('debit', DECIMAL, nullable=True)  # 贷
    # 待定
    extorder = Column('extorder', String(128), nullable=True)  # 第三方单号
    comment = Column('comment', String(4096), nullable=True)  # 备注
    extpay_id = Column('extpay_id', String(32), nullable=True)  # 支付源
    exchange = Column('exchange', DECIMAL, nullable=True)  # 汇率
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间

    def __init__(self, uid, _type, mtlogin, transaction, extorder, comment, extpay_id, exchange, credit, debit,
                 _id=None):
        if _id:
            self.id = _id
        self.uid = uid
        self.type = _type
        self.mtlogin = mtlogin
        self.transaction = transaction
        self.extorder = extorder
        self.comment = comment
        self.extpay_id = extpay_id
        self.exchange = exchange
        self.credit = credit
        self.debit = debit


class TFundtype(BaseDB):
    """
    类TFundtype ORM 表t_fundtype（资金变动类型）
    """
    __tablename__ = 't_fundtype'

    type = Column('type', BigInteger, primary_key=True, autoincrement=True, nullable=False)  # 客户资金变动类型表: 类型ID
    name = Column('name', CHAR(128), nullable=False)  # 类型名称
    ename = Column('ename', CHAR(128), nullable=False)  # 类型英文名称


class TExtpay(BaseDB):
    """
    类TExtpay ORM 表t_extpay（支付源）
    """
    __tablename__ = 't_extpay'

    id = Column('id', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # 支付源表: 支付源id
    name = Column('name', String(64), nullable=False)  # 类型名称
    gateway = Column('gateway', String(512), nullable=False)  # 网关接口
    appid = Column('appid', String(512), nullable=False)  # AppID
    key = Column('key', String(512), nullable=False)  # Key

    def __init__(self, name, gateway):
        self.name = name
        self.gateway = gateway


class TConfig(BaseDB):
    """
    类TConfig ORM 表t_config（系统参数）
    """
    __tablename__ = 't_config'

    name = Column('name', String(32), primary_key=True, nullable=False)  # 系统参数表: 参数项
    value = Column('value', CHAR(1024), nullable=True)  # 参数值
    comment = Column('comment', String(1024), nullable=True)  # 备注

    def __init__(self, name, value, content):
        self.name = name
        self.value = value
        self.content = content


class TAccess(BaseDB):
    """
    类TAccess ORM 表t_access（权限）
    """
    __tablename__ = 't_access'

    id = Column('id', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # 权限表: 权限id
    name = Column('name', String(64), nullable=False)  # 权限名称
    url = Column('url', String(256), nullable=False)  # 容器URL
    element = Column('element', String(128), nullable=True)  #
    """
    type: 
    三位字符串串,每位取值为1/0,1表示yes,0表示no  
    三位表示,对于url:         [get] [post] [无效] 
    三位表示,对于element:     [可显示] [可输入/选择] [submit]
    例:101 - 表示⼀一个按钮可见并且可以点击;110表示⼀一个checkbox可见并且可以选择
    """
    type = Column('type', String(3), nullable=False)  # 权限类型
    menu1 = Column('menu1', String(128), nullable=True, default=False)  # 菜单项1
    menu2 = Column('menu2', String(128), nullable=True, default=False)  # 菜单项2
    target = Column('target', String(64), nullable=True, default=False)  # 菜单方式
    description = Column('description', String(1024), nullable=True)  # 说明
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, name, url, element, _type, menu1, menu2, description):
        self.name = name
        self.url = url
        self.element = element
        self.type = _type
        self.menu1 = menu1
        self.menu2 = menu2
        self.description = description


class TRole(BaseDB):
    """
    类TRole ORM 表t_role（角色）
    """
    __tablename__ = 't_role'

    id = Column('id', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # 角色表: 角色id
    name = Column('name', String(64), nullable=False)  # 角色名称
    access = Column('access', ARRAY(String), nullable=True)  # 角色权限
    # 系统角色(缺省值为false,该值为true的记录,在管理员页面不可编辑)
    builtin = Column('builtin', Boolean, default=False, nullable=False)
    description = Column('description', String(1024), nullable=True)  # 说明
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, name, access, builtin, description):
        self.name = name
        self.access = access
        self.builtin = builtin
        self.description = description


class TTask(BaseDB):
    """
    类TTask ORM 表t_task（任务）
    """
    __tablename__ = 't_task'

    type = Column('type', CHAR(32), primary_key=True, nullable=False,
                  server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # Task类表: id
    name = Column('name', String(64), nullable=False)  # 类型名称
    trigger = Column('trigger', CHAR(128), nullable=False)  # 发起者URL
    success = Column('success', CHAR(128), nullable=False)  # 成功触发
    fail = Column('fail', String(128), nullable=False)  # 失败触发
    subject = Column('subject', String(128), nullable=True)  # 标题
    body = Column('body', Text, nullable=True)  # 内容文本
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, name, trigger, success, fail, subject, body):
        self.name = name
        self.trigger = trigger
        self.success = success
        self.fail = fail
        self.subject = subject
        self.body = body


class TTaskNode(BaseDB):
    """
    类TTaskNode ORM 表t_tasknode（任务节点）
    """
    __tablename__ = 't_tasknode'

    id = Column('id', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # Task节点表: id
    previous = Column('previous', CHAR(32), nullable=True)  # 上一个节点ID
    name = Column('name', String(64), nullable=False)  # 节点名称
    t_type = Column('t_type', CHAR(32), nullable=False)  # 所属Task类
    approve = Column('approve', String(128), nullable=False)  # approve命名
    returned = Column('returned', String(128), nullable=True)  # 被return命名
    step = Column('step', Integer, nullable=False)  # 节点阶段
    canapprove = Column('canapprove', Boolean, nullable=False)  # approve可用
    canreturn = Column('canreturn', Boolean, nullable=False)  # return可用
    canreject = Column('canreject', Boolean, nullable=False)  # reject可用
    role_id = Column('role_id', CHAR(32), nullable=True)  # 处理者role
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, previous, name, t_type, approve, returned, step, canapprove, canreturn, canreject, role_id):
        self.previous = previous
        self.name = name
        self.t_type = t_type
        self.approve = approve
        self.returned = returned
        self.step = step
        self.canapprove = canapprove
        self.canreturn = canreturn
        self.canreject = canreject
        self.role_id = role_id


class TTaskItem(BaseDB):
    """
    类TTaskItem ORM 表t_taskitem（任务条款）
    """
    __tablename__ = 't_taskitem'

    id = Column('id', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # Task表: 任务id
    t_type = Column('t_type', CHAR(32), nullable=False)  # 类型
    o_uid = Column('o_uid', CHAR(32), nullable=False)  # 发起人
    source_uid = Column('source_uid', CHAR(32), nullable=True)  # 源用户
    target_uid = Column('target_uid', CHAR(32), nullable=True)  # 目的用户
    sourcemt = Column('sourcemt', String(10), nullable=True)  # 源MT账户
    targetmt = Column('targetmt', String(10), nullable=True)  # 目的MT账户
    mtgroup = Column('mtgroup', String(64), nullable=True)  # MT分组
    state = Column('state', String(16), nullable=False)  # 状态(queue=待审批, returned=被退回, finished=结束, reject=终⽌)
    tasknode_id = Column('tasknode_id', CHAR(32), nullable=True)  # 当前节点
    amount = Column('amount', DECIMAL, nullable=True)  # 金额
    exchange = Column('exchange', DECIMAL, nullable=True)  # 汇率
    points = Column('points', Integer, nullable=True)  # 点数
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount,
                 exchange, points):
        self.t_type = t_type
        self.o_uid = o_uid
        self.source_uid = source_uid
        self.target_uid = target_uid
        self.sourcemt = sourcemt
        self.targetmt = targetmt
        self.mtgroup = mtgroup
        self.state = state
        self.tasknode_id = tasknode_id
        self.amount = amount
        self.exchange = exchange
        self.points = points


class TTaskHistory(BaseDB):
    """
    类TTaskHistory ORM 表t_taskhistory（任务历史）
    """
    __tablename__ = 't_taskhistory'

    id = Column('id', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # Task历史表: 历史id
    taskitem = Column('taskitem', CHAR(32), nullable=False)  # 任务id
    oprator = Column('oprator', CHAR(32), nullable=False)  # 操作者
    change = Column('change', String(16), nullable=False)  # 状态改变 state:{"new", "approve", "returned", "reject"}
    tasknode_id = Column('tasknode_id', CHAR(32), nullable=True)  # 节点
    comment = Column('comment', String(4096), nullable=False)  # 注释
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间

    def __init__(self, taskitem, oprator, change, tasknode_id, comment):
        self.taskitem = taskitem
        self.oprator = oprator
        self.change = change
        self.tasknode_id = tasknode_id
        self.comment = comment


class TMessage(BaseDB):
    """
    类TMessage ORM 表t_message（消息）
    """
    __tablename__ = 't_message'

    type = Column('type', CHAR(32), primary_key=True, nullable=False)  # Message表: 类型
    name = Column('name', String(64), nullable=False)  # 类型名称
    trigger = Column('trigger', String(128), nullable=False)  # 发起者URL
    role_id = Column('role_id', CHAR(32), nullable=True)  # 接收者role
    subject = Column('subject', String(128), nullable=False)  # 标题
    body = Column('body', Text, nullable=False)  # 内容文本
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, type, name, role_id, subject, body):
        self.type = type
        self.name = name
        self.role_id = role_id
        self.subject = subject
        self.body = body


class TMessageItem(BaseDB):
    """
    类TMessageItem ORM 表t_messageitem（消息条款）
    """
    __tablename__ = 't_messageitem'

    id = Column('id', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # Message表: id
    m_type = Column('m_type', CHAR(32), nullable=False)  # 类型
    o_uid = Column('o_uid', CHAR(32), nullable=False)  # 发起人
    source_uid = Column('source_uid', CHAR(32), nullable=True)  # 源用户
    target_id = Column('target_id', CHAR(32), nullable=True)  # 目的用户
    sourcemt = Column('sourcemt', String(10), nullable=True)  # 源MT账户
    targetmt = Column('targetmt', String(10), nullable=True)  # 目的MT账户
    amount = Column('amount', DECIMAL, nullable=True)  # 金额
    points = Column('points', Integer, nullable=True)  # 点数
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间

    def __init__(self, m_type, o_uid, source_uid, target_id, sourcemt, targetmt, amount, points):
        self.m_type = m_type
        self.o_uid = o_uid
        self.source_uid = source_uid
        self.target_id = target_id
        self.sourcemt = sourcemt
        self.targetmt = targetmt
        self.amount = amount
        self.points = points


class TAudit(BaseDB):
    """
    类TAudit ORM 表t_audit（审计）
    """
    __tablename__ = 't_audit'

    id = Column('id', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # 审计表: id
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间

    def __init__(self):
        pass


class TGroup(BaseDB):
    """
    类TGroup ORM 表t_group（用户分组）
    """
    __tablename__ = 't_group'

    id = Column('gid', CHAR(32), primary_key=True, nullable=False,
                server_default=text("replace(gen_random_uuid()::text, '-', '')"))  # 用户分组表: id
    gname = Column('gname', String(64), nullable=False)  # 组名称

    def __init__(self, gname):
        self.gname = gname


class TMTGroup(BaseDB):
    """
    类TMTGroup ORM 表t_mtgroup（MT分组）
    """
    __tablename__ = 't_mtgroup'

    name = Column('name', String(64), primary_key=True, nullable=False)  # MT分组表:组名
    mtname = Column('mtname', String(64), nullable=False)  # MT名
    type = Column('type', Integer, nullable=False)  # 类型(1:标准组,2:专业组,3:VIP组,0:特殊组)
    spread = Column('spread', Integer, nullable=False)  # 内佣加点
    commission = Column('commission', Integer, nullable=False)  # 外佣加点
    leverage = Column('leverage', DECIMAL, nullable=False)  # 杠杆率
    maxbalance = Column('maxbalance', DECIMAL, nullable=True)  # 资金上限
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, name, mtname, _type, spread, commission, leverage, maxbalance):
        self.name = name
        self.mtname = mtname
        self.type = _type
        self.spread = spread
        self.commission = commission
        self.leverage = leverage
        self.maxbalance = maxbalance


class TMTGrouptype(BaseDB):
    """
    类TMTGrouptype ORM 表t_mtgrouptype（MT分组类型）
    """
    __tablename__ = 't_mtgrouptype'
    # 1=标准组,2=专业组,3=VIP组,0=特殊组
    type = Column('type', Integer, primary_key=True, nullable=False)  # MT分组类型表: 类型
    name = Column('name', String(64), nullable=False)  # 名称
    ename = Column('ename', String(64), nullable=False)  # 英文名称

    def __init__(self, type, name, ename):
        self.type = type
        self.name = name
        self.ename = ename


class TSymbolfactor(BaseDB):
    """
    类TSymbolfactor ORM 表t_symbolfactor（产品佣金比例关系）
    """
    __tablename__ = 't_symbolfactor'

    symbol = Column('symbol', String(16), primary_key=True, nullable=False)  # 产品佣金比例关系表: 产品名
    group = Column('group', String(64), nullable=False)  # 产品分组
    factor = Column('factor', DECIMAL, nullable=False)  # 比例系数
    maxreward = Column('maxreward', DECIMAL, nullable=False)  # 返点最大值
    quote = Column('quote', String(32), nullable=False)  # 交叉盘汇率取值
    formula = Column('formula', Integer, nullable=False)  # 计算公式类型
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间

    def __init__(self, symbol, group, factor):
        self.symbol = symbol
        self.group = group
        self.factor = factor


class VSymbolfactor(BaseDB):
    """
    类VSymbolfactor ORM 表v_symbolfactor（产品佣金比例关系视图）
    """
    __tablename__ = 'v_symbolfactor'

    symbol = Column('symbol', String(16), primary_key=True, nullable=False)  # 产品佣金比例关系视图 : 品种
    factor = Column('factor', DECIMAL, nullable=False)  # 比例系数
    maxreward = Column('maxreward', DECIMAL, nullable=False)  # 返点最大值
    formula = Column('formula', Integer, nullable=False)  # 计算公式类型
    quoteprise = Column('quoteprise', DECIMAL, nullable=False)  # 计算公式类型
    multiply = Column('multiply', DECIMAL, nullable=False)  # 计算公式类型
    contractsize = Column('contractsize', String(16), nullable=False)  # 计算公式类型
    reward0 = Column('reward0', DECIMAL, nullable=False)  # 计算公式类型
    reward1 = Column('reward1', DECIMAL, nullable=False)  # 计算公式类型
    reward2 = Column('reward2', DECIMAL, nullable=False)  # 计算公式类型


class VTaskitem(BaseDB):
    """
    类VTaskitem ORM 表v_taskitem（任务一览视图）
    """
    __tablename__ = 'v_taskitem'

    id = Column('id', CHAR(32), primary_key=True, nullable=False)  # 任务一览视图: 任务id
    subject = Column('subject', String(128), nullable=True)  # 任务标题
    taskname = Column('taskname', String(64), nullable=True)  # 任务名称
    body = Column('body', String(2048), nullable=True)  # 任务内容⽂本
    o_uid = Column('o_uid', String(32), nullable=True)  # 发起⼈
    o_cname = Column('o_cname', String(64), nullable=True)  # 发起⼈姓名
    source_uid = Column('source_uid', String(32), nullable=True)  # 源⽤户
    source_cname = Column('source_cname', String(64), nullable=True)  # 源⽤户姓名
    target_uid = Column('target_uid', String(32), nullable=True)  # ⽬的⽤户
    target_cname = Column('target_cname', String(64), nullable=True)  # 目的用户姓名
    sourcemt = Column('sourcemt', String(10), nullable=True)  # 源MT账户
    targetmt = Column('targetmt', String(10), nullable=True)  # ⽬的MT账户
    mtgroup = Column('mtgroup', String(64), nullable=True)  # MT分组
    amount = Column('amount', DECIMAL, nullable=True)  # ⾦额
    exchange = Column('exchange', DECIMAL, nullable=True)  # 汇率
    points = Column('points', Integer, nullable=True)  # 点数
    state = Column('state', String(16), nullable=True)  # 状态
    tasknode_id = Column('tasknode_id', String(32), nullable=True)  # 当前节点id
    createtime = Column('createtime', TIMESTAMP, nullable=True)  # 任务创建时间
    updatetime = Column('updatetime', TIMESTAMP, nullable=True)  # 上次修改时间
    nodename = Column('nodename', String(64), nullable=True)  # 当前节点名称
    step = Column('step', Integer, nullable=True)  # 当前节点阶段
    approve = Column('approve', String(128), nullable=True)  # approve命名
    returned = Column('returned', String(128), nullable=True)  # 被return命名
    canapprove = Column('canapprove', Boolean, nullable=True)  # approve可⽤
    canreturn = Column('canreturn', Boolean, nullable=True)  # return可⽤
    canreject = Column('canreject', Boolean, nullable=True)  # reject可⽤
    role_id = Column('role_id', String(32), nullable=True)  # 处理者role
    success = Column('success', String(128), nullable=True)  # success调用
    fail = Column('fail', String(128), nullable=True)  # fail调用


class VInternaluser(BaseDB):
    """
    类VInternaluser ORM 表v_internaluser（内部客户视图）
    """
    __tablename__ = 'v_internaluser'

    uid = Column('uid', CHAR(32), primary_key=True, nullable=False)  # 内部用户视图: 内部用户id
    passwd = Column('passwd', String(64), nullable=True)  # 密码
    email = Column('email', String(64), nullable=True)  # 电子邮箱
    gid = Column('gid', String(32), nullable=True)  # 用户分组
    role_id = Column('role_id', String(32), nullable=True)  # 用户角色
    report = Column('report', String(32), nullable=True)  # 用户经理
    status = Column('status', String(128), nullable=True)  # 用户状态
    createtime = Column('createtime', TIMESTAMP, server_default=func.now(), nullable=False)  # 创建时间
    updatetime = Column('updatetime', TIMESTAMP, server_default=func.now(), onupdate=func.now(),
                        nullable=False)  # 上次修改时间


class VCommission(BaseDB):
    """
    类VCommission ORM 表v_commission（佣金视图）
    """
    __tablename__ = 'v_commission'

    id = Column('id', CHAR(32), primary_key=True, nullable=False)  # 佣金视图
    uid = Column('uid', CHAR(32), nullable=False)  # 佣金视图: 客户id
    email = Column('email', String(64), nullable=True)  # 电⼦邮箱
    mobile = Column('mobile', String(32), nullable=True)  # ⼿机号
    agent_id = Column('agent_id', String(8), nullable=True)  # 上级代理商编码
    cname = Column('cname', String(64), nullable=True)  # 姓名
    mtlogin = Column('mtlogin', String(10), nullable=True)  # MT账户
    spread = Column('spread', Integer, nullable=True)  # 内佣加点
    commission = Column('commission', Integer, nullable=True)  # 外佣
    agent_id1 = Column('agent_id1', String(8), nullable=True)  # 上⼀级代理id
    reward1 = Column('reward1', Integer, nullable=True)  # 上⼀级代理返佣
    agent_id2 = Column('agent_id2', String(8), nullable=True)  # 上⼆级代理id
    reward2 = Column('reward2', Integer, nullable=True)  # 上⼆级代理返佣
    agent_id3 = Column('agent_id3', String(8), nullable=True)  # 上三级代理id
    reward3 = Column('reward3', Integer, nullable=True)  # 上三级代理返佣


class VMtgroup(BaseDB):
    """
    类VMtgroup ORM 表v_mtgroup（MT原始组视图）
    """
    __tablename__ = 'v_mtgroup'

    mtname = Column('uid', String(64), primary_key=True, nullable=True)  # MT原始组视图: 客户id
    leverage = Column('mtlogin', DECIMAL, nullable=True)  # MT账户


class VMtuser(BaseDB):
    """
    类VMtuser ORM 表v_mtuser（MT账号一览视图）
    """
    __tablename__ = 'v_mtuser'

    id = Column('id', CHAR(32), primary_key=True, nullable=False)  # MT账号一览视图
    uid = Column('uid', CHAR(32), nullable=False)  # MT账户一览视图: 客户id
    mtlogin = Column('mtlogin', DECIMAL, nullable=True)  # MT账户
    mtgroup = Column('mtgroup', String(64), nullable=True)  # MT分组
    leverage = Column('leverage', DECIMAL, nullable=True)  # 杠杆率
    balance = Column('balance', DECIMAL, nullable=True)  # 账户结余
    marginlevel = Column('marginlevel', DECIMAL, nullable=True)  # 预付款维持率
    equity = Column('equity', DECIMAL, nullable=True)  # 账户净值
    type = Column('type', Integer, nullable=True)  # 账户类型
    groupname = Column('groupname', String(64), nullable=True)  # MT分组名称
    typename = Column('typename', String(64), nullable=True)  # 账户类型名
    spread = Column('spread', Integer, nullable=True)  # 内佣加点
    commission = Column('commission', Integer, nullable=True)  # 外佣加点
    maxbalance = Column('maxbalance', DECIMAL, nullable=True)  # 资⾦上限


class VDealclosed(BaseDB):
    """
    类VDealclosed ORM 表v_dealclosedr（MT已平仓单视图）
    """
    __tablename__ = 'v_dealclosed'

    id = Column('id', CHAR(32), primary_key=True, nullable=False)  # MT已平仓单视图
    deal = Column('deal', CHAR(32), nullable=False)  # MT已平仓单视图: 成交号
    timestamp = Column('timestamp', TIMESTAMP, nullable=True)  # 时间戳
    login = Column('login', Integer, nullable=True)  # 账户
    order = Column('order', Integer, nullable=True)  # 订单号
    action = Column('action', DECIMAL, nullable=True)  # 交易类型
    entry = Column('entry', DECIMAL, nullable=True)  #
    reason = Column('reason', DECIMAL, nullable=True)  # 执行类型
    digits = Column('digits', DECIMAL, nullable=True)  # 交易品种⼩数位
    digitscurrency = Column('digitscurrency', DECIMAL, nullable=True)  # 保证⾦⼩数位
    contractsize = Column('contractsize', DECIMAL, nullable=True)  # 合约⼤⼩
    time = Column('time', TIMESTAMP, nullable=True)  # 平仓时间
    symbol = Column('symbol', String(32), nullable=True)  # 品种
    price = Column('price', DECIMAL, nullable=True)  # 价格
    volume = Column('volume', Integer, nullable=True)  # 交易量(手数)
    profit = Column('profit', DECIMAL, nullable=True)  # 利润
    storage = Column('storage', DECIMAL, nullable=True)  # 过夜利息
    commission = Column('commission', DECIMAL, nullable=True)  # 外佣
    rateprofit = Column('rateprofit', DECIMAL, nullable=True)  # 利润率
    positionid = Column('positionid', Integer, nullable=True)  # 飘单号
    priceposition = Column('priceposition', DECIMAL, nullable=True)  #
    volumeclosed = Column('volumeclosed', Integer, nullable=True)  # 平仓量(手数)
    # reward1, reward2, reward3为代理商实得之返佣点数，已记⼊内佣加点和扣除层级分成
    tickvalue = Column('tickvalue', Integer, nullable=True)  #
    ticksize = Column('ticksize', Integer, nullable=True)  #
    agent_id1 = Column('agent_id1', Integer, nullable=True)  # 上⼀级代理id
    reward1 = Column('reward1', Integer, nullable=True)  # 上⼀级代理返佣
    agent_id2 = Column('agent_id2', Integer, nullable=True)  # 上⼆级代理id
    reward2 = Column('reward2', Integer, nullable=True)  # 上⼆级代理返佣
    agent_id3 = Column('agent_id3', Integer, nullable=True)  # 上三级代理id
    reward3 = Column('reward3', Integer, nullable=True)  # 上三级代理返佣
    factor = Column('factor', Integer, nullable=True)  # 系数


class VFxusdcnh(BaseDB):
    """
    类VFxusdcnh ORM 表v_fxusdcnh（人民币汇率视图）
    """
    __tablename__ = 'v_fxusdcnh'

    id = Column('id', CHAR(32), primary_key=True, nullable=False)  # 人民币汇率视图
    depositfx = Column('depositfx', DECIMAL, nullable=False)  # ⼊⾦汇率
    withdrawfx = Column('withdrawfx', DECIMAL, nullable=False)  # 出⾦汇率


class VClient(BaseDB):
    """
    类VClient ORM 表v_client（客户视图）
    """
    __tablename__ = 'v_client'

    id = Column('id', CHAR(32), primary_key=True, nullable=False)  # 客户视图
    uid = Column('uid', String(32), nullable=False)  # 用户id
    cname = Column('cname', String(64), nullable=False)  # 中文姓名
    mobile = Column('mobile', String(32), nullable=False)  # 手机号
    email = Column('email', String(64), nullable=False)  # 电子邮箱
    certid = Column('certid', String(128), nullable=False)  # 证件号
    bankaccount = Column('bankaccount', String(32), nullable=False)  # 银行账户
    mtlogin = Column('mtlogin', ARRAY(String), nullable=False)  # MT账户
    statusa = Column('statusa', String(128), nullable=False)  # 用户状态A
    createtime = Column('createtime', String(8), nullable=False)  # ⽤户创建时间
    agentid = Column('agentid', String(8), nullable=False)  # 代理商编码
    agent = Column('agent', String(8), nullable=False)  # 代理商编码
    parentid = Column('parentid', String(8), nullable=False)  # 上级代理
    a_level = Column('a_level', String(8), nullable=False)  # 代理商层级
    a_status = Column('a_status', String(8), nullable=False)  # 代理商状态
    a_createtime = Column('a_createtime', String(8), nullable=False)  # 代理商创建时间


class VDealhistory(BaseDB):
    """
    VDealhistory ORM 表v_dealhistory（成交历史视图）
    """
    __tablename__ = 'v_dealhistory'

    id = Column('id', CHAR(32), primary_key=True, nullable=False)  # MT成交历史视图
    uid = Column('uid', String(32), nullable=False)  # 用户id
    deal = Column('deal', DECIMAL, nullable=False)  # 成交号
    timestamp = Column('timestamp', TIMESTAMP, nullable=False)  # 时间戳
    login = Column('login', DECIMAL, nullable=False)  # MT账号
    order = Column('order', DECIMAL, nullable=False)  # 订单号
    action = Column('action', DECIMAL, nullable=False)  # 类型
    entry = Column('entry', DECIMAL, nullable=False)  # 方向
    reason = Column('reason', DECIMAL, nullable=False)  # 执行类型
    digits = Column('digits', DECIMAL, nullable=False)  # 交易品种小数位
    digitscurrency = Column('digitscurrency', DECIMAL, nullable=False)  # 保证金小数位
    contractsize = Column('contractsize', Float, nullable=False)  # 合约大小
    time = Column('time', TIMESTAMP, nullable=False)  # 时间
    symbol = Column('symbol', String(32), nullable=False)  # 品种
    price = Column('price', Float, nullable=False)  # 成交价
    volume = Column('volume', DECIMAL, nullable=False)  # 交易量
    profit = Column('profit', Float, nullable=False)  # 利润
    storage = Column('storage', Float, nullable=False)  # 库存量
    commission = Column('commission', Float, nullable=False)  # 外佣（手续费）
    rateprofit = Column('rateprofit', Float, nullable=False)  # 利润率
    positionid = Column('positionid', DECIMAL, nullable=False)  # 票单号
    profitraw = Column('profitraw', Float, nullable=False)  # 净利润
    priceposition = Column('priceposition', Float, nullable=False)  # 开仓价格
    volumeclosed = Column('volumeclosed', DECIMAL, nullable=False)  # 平仓量（手数）
    tickvalue = Column('tickvalue', DECIMAL, nullable=False)
    ticksize = Column('ticksize', DECIMAL, nullable=False)


class VTradehistory(BaseDB):
    """
    VTradehistory ORM 表v_tradehistory（交易历史视图）
    """
    __tablename__ = 'v_tradehistory'

    id = Column('id', CHAR(32), primary_key=True, nullable=False)  # MT交易历史视图
    uid = Column('uid', String(32), nullable=False)  # 用户id
    o_deal = Column("o_deal", DECIMAL, nullable=False)  # 开仓成交号
    o_timestamp = Column('o_timestamp', TIMESTAMP, nullable=False)  # 开仓时间戳
    login = Column("login", DECIMAL, nullable=False)  # MT账号
    o_order = Column('o_order', DECIMAL, nullable=False)  # 开仓订单号
    o_action = Column("o_action", DECIMAL, nullable=False)  # 开仓交易类型
    o_entry = Column('o_entry', DECIMAL, nullable=False)  # 开仓交易方向
    o_reason = Column('o_reason', DECIMAL, nullable=False)  # 开仓执行类型
    contractsize = Column('contractsize', Float, nullable=False)  # 合约⼤小
    o_time = Column("o_time", TIMESTAMP, nullable=False)  # 开仓时间
    symbol = Column("symbol", String(32), nullable=False)  # 品种
    o_price = Column("o_price", Float, nullable=False)  # 开仓价格
    volume = Column("volume", DECIMAL, nullable=False)  # 开仓交易量
    o_commission = Column("o_commission", Float, nullable=False)  # 开仓外佣
    positionid = Column("positionid", DECIMAL, nullable=False)  # 飘单号
    c_deal = Column("c_deal", DECIMAL, nullable=False)  # 平仓成交号
    c_timestamp = Column('c_timestamp', TIMESTAMP, nullable=False)  # 平仓时间戳
    c_order = Column('c_order', DECIMAL, nullable=False)  # 平仓订单号
    c_action = Column('c_action', DECIMAL, nullable=False)  # 平仓交易类型
    c_entry = Column('c_entry', DECIMAL, nullable=False)  # 平仓交易方向
    c_reason = Column('c_reason', DECIMAL, nullable=False)  # 平仓执行类型
    c_time = Column("c_time", TIMESTAMP, nullable=False)  # 平仓成交时间
    c_price = Column("c_price", Float, nullable=False)  # 平仓价格
    profit = Column("profit", Float, nullable=False)  # 利润
    storage = Column("storage", Float, nullable=False)  # 过夜利息
    c_commission = Column("c_commission", Float, nullable=False)  # 平仓外佣
    rateprofit = Column('rateprofit', Float, nullable=False)  # 利润率
    profitraw = Column("profitraw", Float, nullable=False)  # 净利润
    volumeclosed = Column('volumeclosed', DECIMAL, nullable=False)  # 平仓量(手数)


class VOpenposition(BaseDB):
    """
    VOpenposition ORM 表v_openposition（票单视图）
    """
    __tablename__ = 'v_openposition'

    id = Column('id', CHAR(32), primary_key=True, nullable=False)  # MT票单视图
    uid = Column('uid', String(32), nullable=False)  # 用户id
    position = Column("position", DECIMAL, nullable=False)  # 开仓成交号
    login = Column("login", DECIMAL, nullable=False)  # MT账号
    timestamp = Column('timestamp', TIMESTAMP, nullable=False)  # 时间戳
    symbol = Column("symbol", String(32), nullable=False)  # 品种
    action = Column("action", DECIMAL, nullable=False)  # 交易类型
    digits = Column('digits', DECIMAL, nullable=False)  # 交易品种小数位
    digitscurrency = Column('digitscurrency', DECIMAL, nullable=False)  # 保证金小数位
    reason = Column('reason', DECIMAL, nullable=False)  # 执行类型
    contractsize = Column('contractsize', Float, nullable=False)  # 合约⼤小
    timecreate = Column("timecreate", TIMESTAMP, nullable=False)  # 开仓时间
    timeupdate = Column("timeupdate", TIMESTAMP, nullable=False)  # 更新时间
    priceopen = Column("priceopen", Float, nullable=False)  # 开仓价格
    pricecurrent = Column("pricecurrent", Float, nullable=False)  # 当前价格
    pricesl = Column("pricesl", Float, nullable=False)  # ⽌损价格
    pricetp = Column("pricetp", Float, nullable=False)  # ⽌盈价格
    volume = Column("volume", DECIMAL, nullable=False)  # 交易量
    profit = Column("profit", Float, nullable=False)  # 利润
    storage = Column("storage", Float, nullable=False)  # 过夜利息
    rateprofit = Column('rateprofit', Float, nullable=False)  # 利润率


def tables():
    return [TUser.__table__,
            TPic.__table__,
            TAgent.__table__,
            TFundflow.__table__,
            TExtpay.__table__,
            TConfig.__table__,
            TAccess.__table__,
            TRole.__table__,
            TTask.__table__,
            TTaskNode.__table__,
            TTaskItem.__table__,
            TTaskHistory.__table__,
            TMessage.__table__,
            TMessageItem.__table__,
            TAudit.__table__,
            TGroup.__table__,
            TMTGroup.__table__,
            TSymbolfactor.__table__]


def init_db():
    BaseModel.metadata.create_all(bind=db, tables=tables())


def drop_db():
    BaseModel.metadata.drop_all(bind=db, tables=tables())
