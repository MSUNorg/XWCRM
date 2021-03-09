#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: outerCustomer.py
@time: 18/6/15 15:12
@description: 外部终端客户操作
"""

import decimal
from base import *
from utils import lizhipay, utils
from utils.utils import parser_date, format_date

logger = logging.getLogger('xwcrm.outerCustomer')


# 交易账号管理
# 客户资金变动类型
class FundtypeHandler(ApiHandler):
    def get(self):
        uid = self.current_user.uid
        types = self.fundflowDao.select_types_by_uid_distinct(uid)
        fundtypes = self.fundtypeDao.select_all()
        res = []
        for fundtype in fundtypes:
            if fundtype.type in types:
                res.append({"type": fundtype.type, "name": fundtype.name, "ename": fundtype.ename})
        self.suc({"fundtypes": res})
        return


# 交易账户类型
class GrouptypeHandler(ApiHandler):
    def get(self):
        grouptype = self.mtgrouptypeDao.select_new_user()
        grouptypes = [{"type": grouptype.name, "typeename": grouptype.ename}]
        self.suc({"grouptypes": grouptypes})
        return


# 提交新创建交易账户
class MTAddHandler(ApiHandler):
    def post(self):
        _type = self.get_json_argument('type', default=None)

        if not _type:
            # self.error(u'请选择类型')
            self.error(u'Please select type.')
            return
        _user = self.current_user
        _mtusers = self.vmtuserDao.select_by_uid(_user.uid)
        if _user.statusa == u'集群':
            if len(_mtusers) >= 100:
                # self.error(u'交易账户已达上限')
                self.error(u'Too many MT accounts have been created.')
                return
        else:
            if len(_mtusers) >= 3:
                # self.error(u'交易账户已达上限')
                self.error(u'Too many MT accounts have been created.')
                return
        _mtlogin = self.vmtuserDao.select_max_login() + 1
        vmtuser = self.vmtuserDao.select_by_uid_first(_user.uid)
        mtlogin = str(_mtlogin)
        mtpasswd = utils.create_str_code()
        mtgroupstr = vmtuser.mtgroup
        mtgroupstr = mtgroupstr.replace('\\', '\\\\')
        if not self.mtDao.doCreate(mtlogin, mtpasswd, mtgroup=mtgroupstr):
            # self.error(u'内部错误')
            self.error(u'Failed to create MT5 account, please contact customer service.')
            return

        mtlogins = _user.mtlogin
        mtls = []
        for mtuser in mtlogins:
            mtls.append(mtuser)
        mtls.append(mtlogin)
        self.userDao.update_mtloginids(_user.uid, mtls)
        _mt = [
            {"mtlogin": mtlogin, "mtpasswd": mtpasswd, "balance": "{:.6f}".format(decimal.Decimal('0.0'))}
        ]
        self.success("mt add success", {"mt": _mt})
        return


# 更新交易账户
class MTUpHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        # _type = self.get_json_argument('type', default=None)
        leverage = self.get_json_argument('leverage', default=None)

        if not mtlogin:
            # self.error(u'请输入交易账户')
            self.error(u'Please enter MT5 account.')
            return
        """
        if not _type:
            self.error(u'请输入类型')
            return
        """
        if not leverage:
            # self.error(u'请选择交易杠杆比例')
            self.error(u'Please select leverage.')
            return
        v_mtuser_objs = self.vmtuserDao.select_by_mtlogin(mtlogin)  # 感觉没必要all啊，返回应该是one or null
        for v_mtuser_obj in v_mtuser_objs:
            mtname = self.mtgroupDao.select_mtname(v_mtuser_obj.type, v_mtuser_obj.spread, v_mtuser_obj.commission,
                                                   leverage)
            if not mtname:
                # self.error(u'内部错误')
                self.error(u'Internal error')
                return
            if not self.mtDao.doGroup(mtlogin, leverage, mtname):
                # self.error(u'内部错误')
                self.error(u'Internal error')
                return
        self.success()
        return


# 修改交易密码
class MTPassUpHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        mtpasswd = self.get_json_argument('mtpasswd', default=None)
        mtpasswd_confirm = self.get_json_argument('mtpasswd_confirm', default=None)

        if not mtlogin:
            # self.error(u'请输入交易账户')
            self.error(u'Please enter MT5 account.')
            return
        if not mtpasswd:
            # self.error(u'请输入密码')
            self.error(u'Please enter password.')
            return
        if mtpasswd != mtpasswd_confirm:
            # self.error(u'两次密码不一致')
            self.error(u'Password entered is inconsistent.')
            return

        if not self.mtDao.doPasswd(mtlogin, mtpasswd):
            # self.error(u'内部错误')
            self.error(u'Failed to change MT5 password, please contact customer service.')
            return
        self.success()
        return


# 已平仓交易记录
class MTRecordHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        symbol = self.get_json_argument('symbol', default=None)
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument('page', default=None)

        if not mtlogin:
            # self.error(u'请输入交易账户')
            self.error(u'Please enter MT5 account.')
            return
        if not symbol:
            # self.error(u'请选择交易品种')
            self.error(u'Please select symbol.')
            return

        pagination = self.vdealclosedDao.select_login_symbol(mtlogin, symbol, parser_date(start, "%Y-%m-%d"),
                                                             parser_date(end, "%Y-%m-%d"), page)
        _objs = []
        for rec in pagination.items:
            _objs.append(
                {"deal": str(rec.deal), "login": str(rec.login), "order": str(rec.order),
                 "action": str(rec.action), "entry": str(rec.entry), "reason": str(rec.reason),
                 "time": format_date(rec.time),
                 "symbol": str(rec.symbol), "price": str(rec.price), "volume": str(rec.volume),
                 "profit": str(rec.profit),
                 "storage": str(rec.storage), "commission": str(rec.commission), "rateprofit": str(rec.rateprofit),
                 "positionid": str(rec.positionid), "priceposition": str(rec.priceposition),
                 "volumeclosed": str(rec.volumeclosed)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 账户信息
class MTInfoHandler(ApiHandler):
    def get(self):
        _user = self.current_user
        _mtusers = self.vmtuserDao.select_by_uid(_user.uid)
        _mt = []
        for mtuser in _mtusers:
            _mt.append({"mtlogin": str(mtuser.mtlogin), "mtgroup": mtuser.mtgroup, "type": mtuser.type,
                        "leverage": "{:.6f}".format(mtuser.leverage), "typename": mtuser.typename,
                        "balance": "{:.6f}".format(mtuser.balance), "marginlevel": "{:.6f}".format(mtuser.marginlevel),
                        "equity": "{:.6f}".format(mtuser.equity)})
        self.suc({"mt": _mt})
        return


# 财务管理
# MT杠杆率查询,查看加佣,查看加点
class LeverageHandler(ApiHandler):
    def get(self):
        leverages = self.mtgroupDao.select_leverage()
        commissions = self.mtgroupDao.select_commission()
        spreads = self.mtgroupDao.select_spread()
        _leverages = []
        for _leverage in leverages:
            for lev in _leverage:
                _leverages.append("{:.6f}".format(lev))
        self.suc({"leverage": _leverages, "spread": spreads, "commission": commissions})
        return


# 汇率查询
class ExchangeHandler(ApiHandler):
    def get(self):
        exchange = self.vfxusdcnhDao.select_exchange()
        self.suc({"depositfx": "{:.5f}".format(exchange.depositfx), "withdrawfx": "{:.6f}".format(exchange.withdrawfx)})
        return


# 入金
class FinDepositHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        amount_dollar = self.get_json_argument('amount_dollar', default=None)
        amount_rmb = self.get_json_argument('amount_rmb', default=None)
        exchange = self.get_json_argument('exchange', default=None)
        paytype = self.get_json_argument('paytype', default=10)

        if not paytype:
            # self.error(u'请选择入金方式')
            self.error(u'Please select payment method.')
            return
        if not mtlogin:
            # self.error(u'请输入交易账户')
            self.error(u'Please select MT5 account.')
            return
        if not amount_dollar or amount_dollar <= 0:
            # self.error(u'请输入入金金额')
            self.error(u'Please enter the amount.')
            return
        if not amount_rmb or amount_rmb <= 0:
            # self.error(u'请输入入金金额')
            self.error(u'Please enter the amount.')
            return
        if exchange * amount_dollar != amount_rmb:
            self.error(u'交易金额换算错误')
            return
        if not exchange:
            self.error(u'请输入交易汇率')
            return

        _user = self.current_user
        if _user.statusa == '封禁' or _user.statusa == '删除':
            # self.err(905, u'该用户状态异常')
            self.err(905, u'Operation is forbidden.')
            return
        # if _user.statusa == '资⾦冻结' or _user.statusa == '入金冻结':
        if _user.statusa == '入金冻结' or _user.statusa == '审核中':
            # self.err(903, u'该项操作不可⽤')
            self.err(903, u'User status is abnormal.')
            return
        if paytype == 10:  # 10=线上入金,11=电汇入金,20=标准出金,30=内转,50=内佣结算,51=外佣结算
            """
            lastfundflow = self.fundflowDao.select_by_uid(_user.uid)
            if lastfundflow:
            createtime = utils.datetime_timestamp(str(lastfundflow.createtime))
            if ((int(time.time()) - createtime) > 0) and ((int(time.time()) - createtime) < 300) and (lastfundflow.credit <= 0):
            self.error(u'有未完成的订单')
            return
            """
            upper = self.configDao.get_by_name(u'网银入金上限')
            lower = self.configDao.get_by_name(u'网银入金下限')
            if amount_rmb <= lower or amount_rmb >= upper:
                self.error(u'Operation failed')
                return
            # uid, _type, mtlogin, transaction, extorder, comment, extpay_id, exchange, credit=0, debit=0
            _fundflow = self.fundflowDao.add(_user.uid, 19, mtlogin, "", "", "", "lizhipay", exchange,
                                             credit=amount_dollar, debit=0)
            payurl = lizhipay.dopay(_user.uid, mtlogin, _fundflow.id, amount_rmb)
            self.suc({"payurl": payurl, "orderid": str(_fundflow.id)})
            return
        if paytype == 11:  # 11=电汇入金
            singleNumber = self.get_json_argument('singleNumber', default=None)
            if not singleNumber:
                # self.error(u'请输入汇款单号')
                self.error(u'请输入汇款单号')
                return
            # 写入t_taskitem表
            _task = self.taskDao.select_by_trigger("/fin/deposit")
            if not _task:
                # self.error(u'操作失败')
                self.error(u'Operation failed')
                return
            t_type = _task.type
            _tasknode = self.tasknodeDao.select_by_type_step(t_type, 1)
            if not _tasknode:
                # self.error(u'操作失败')
                self.error(u'Operation failed')
                return
            tn_id = _tasknode.id
            # t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points
            _taskitem = self.taskitemDao.add(t_type, _user.uid, _user.uid, _user.uid, mtlogin, mtlogin, None,
                                             "queue", tn_id, amount_dollar, exchange)
            # 写入t_taskhistory表
            self.taskhistoryDao.add(_taskitem.id, _user.uid, "new", tn_id, singleNumber)
            self.success(u'操作成功')
            return
        # self.error(u'操作失败')
        self.error(u'Operation failed')
        return


# 支付状态查询
class FinPayStatusHandler(ApiHandler):
    def post(self):
        orderid = self.get_json_argument('orderid', default=None)
        if not orderid:
            # self.error(u'请输入订单号')
            self.error(u'Please enter payment reference No.')
            return
        _fundflow = self.fundflowDao.select_by_id(orderid)
        if not _fundflow:
            # self.error(u'订单不存在')
            self.error(u'The order does not exist.')
            return
        if not _fundflow.extorder:
            # self.error(u'未支付')
            self.error(u'Unpaid.')
            return
        if (_fundflow.credit <= 0) and _fundflow.extorder:
            # self.err(906, u'支付失败')
            self.err(906, u'Payment Failed.')
            return
        self.success(u'Payment Successful.')
        return


# 交易账号内部转账
class FinTransferHandler(ApiHandler):
    def post(self):
        out_mt = self.get_json_argument('out_mt', default=None)
        in_mt = self.get_json_argument('in_mt', default=None)
        amount = self.get_json_argument('amount', default=None)
        if not out_mt:
            # self.error(u'请选择转出交易账户')
            self.error(u'Please select MT5 account.')
            return
        if not in_mt:
            # self.error(u'请选择转入交易账户')
            self.error(u'Please select MT5 account.')
            return
        if not amount or amount <= 0:
            # self.error(u'请输入转出金额')
            self.error(u'Please enter the withdraw amount.')
            return

        _user = self.current_user
        if _user.statusa == '封禁' or _user.statusa == '删除':
            # self.err(905, u'该用户状态异常')
            self.err(905, u'Operation is forbidden.')
            return
        # if _user.statusa == '入金冻结' or _user.statusa == '资金冻结':
        if _user.statusa == '入金冻结' or _user.statusa == '审核中':
            # self.err(903, u'该项操作不可⽤')
            self.err(903, u'User status is abnormal.')
            return
        _mtusers = self.vmtuserDao.select_by_uid(_user.uid)
        if len(_mtusers) <= 0:
            # self.error(u'交易账户错误')
            self.error(u'MT5 account error.')
            return
        _mt = {}
        for _mtuser in _mtusers:
            _mt[str(_mtuser.mtlogin)] = _mtuser.equity
        if out_mt == "ewallet":
            balance = self.fundflowDao.select_balance(_user.uid)
            logger.error("amount=%s,balance=%s", amount, balance)
            if amount > balance:
                # self.error(u'余额不足')
                self.error(u'Insufficient account balance.')
                return
            isBal = self.mtDao.doBalance(str(in_mt), str(amount), "2", comment="XWCRM deposit")
            if isBal:
                # uid, _type, mtlogin, transaction, extorder, comment, extpay_id, exchange, credit=0, debit=0
                self.fundflowDao.add(_user.uid, 31, in_mt, "", "", "", "", 0, credit=0, debit=amount)
                self.success(u'转账成功')
            else:
                # self.error(u'转账失败')
                self.error(u'Fund transfer failed.')
            return
        out_mt_balance = _mt[str(out_mt)]
        logger.error("amount=%s,out_mt_balance=%s,lt=%s", amount, out_mt_balance, (amount > out_mt_balance))
        if amount > out_mt_balance:
            # self.error(u'余额不足')
            self.error(u'Insufficient account balance.')
            return
        isBal1 = self.mtDao.doBalance(str(out_mt), str(-amount), "2", comment="XWCRM withdrawal")
        isBal2 = self.mtDao.doBalance(str(in_mt), str(amount), "2", comment="XWCRM deposit")
        if isBal1 and isBal2:
            self.fundflowDao.add(_user.uid, 30, out_mt, "", "", "", "", 0, credit=amount, debit=0)
            self.fundflowDao.add(_user.uid, 30, in_mt, "", "", "", "", 0, credit=0, debit=amount)
            self.success(u'转账成功')
        else:
            # self.error(u'转账失败')
            self.error(u'Fund transfer failed.')
        return


# MT出金
class FinMTWithdrawHandler(ApiHandler):
    """
    TRIGGER⻚⾯ 客户出金
    成功触发 MT出⾦模块
    失败触发 更新TASK状态为FAILED
    参数说明
    source_uid 客户id
    target_uid 这里等于上者
    source_mt 出金MT账号
    target_mt 这里等于上者
    amount 出金金额(USD)
    exchange 出金汇率
    成功触发模块需要将source_mt账号里的amount金额扣除，MT注释为"XWCRM withdraw"
    成功触发模块需要根据source_uid账号在t_fundflow表里新建一条如下记录：
    credit=amount, type=20, uid=source_uid, mtlogin=source_mt, exchange=exchange
    成功触发模块将触发一个新的工作流为"会计出金"，o_uid继承自MT出金任务的o_uid
    """

    def post(self):
        target_mt = self.get_json_argument('target_mt', default=None)  # 出金交易账户
        # 账户余额
        amount = self.get_json_argument('amount', default=None)  # 出金金额
        exchange = self.get_json_argument('exchange', default=None)  # 当前汇率
        # 折合人民币
        if not target_mt:
            # self.error(u'请输入出金MT账户')
            self.error(u'Please enter MT5 account.')
            return
        if not amount:
            # self.error(u'请输入出金金额')
            self.error(u'Please enter the withdraw amount.')
            return
        if not exchange:
            # self.error(u'请输入出金汇率')
            self.error(u'Please enter the exchange rate.')
            return

        _user = self.current_user
        if _user.statusa == '封禁' or _user.statusa == '删除':
            # self.err(905, u'该用户状态异常')
            self.err(905, u'Operation is forbidden.')
            return
        # if _user.statusa == '出金冻结' or _user.statusa == '资金冻结':
        if _user.statusa == '出金冻结' or _user.statusa == '审核中':
            # self.err(903, u'该用户状态异常')
            self.err(903, u'User status is abnormal.')
            return
        _mtusers = self.vmtuserDao.select_by_uid(_user.uid)
        if len(_mtusers) <= 0:
            # self.error(u'交易账户错误')
            self.error(u'MT5 account error.')
            return
        _mt = {}
        for _mtuser in _mtusers:
            _mt[str(_mtuser.mtlogin)] = _mtuser.equity
        logger.error("mount=%s,target_mt=%s", amount, target_mt)
        if not _mt[str(target_mt)]:
            # self.error(u'交易账户错误')
            self.error(u'MT5 account error.')
            return
        if amount > _mt[str(target_mt)]:
            # self.error(u'余额不足')
            self.error(u'Insufficient account balance.')
            return
        # 写入t_taskitem表
        _task = self.taskDao.select_by_trigger("/fin/withdraw/mt")
        if not _task:
            # self.error(u'操作失败')
            self.error(u'Operation failed')
            return
        t_type = _task.type
        _tasknode = self.tasknodeDao.select_by_type_step(t_type, 1)
        if not _tasknode:
            # self.error(u'操作失败')
            self.error(u'Operation failed')
            return
        tn_id = _tasknode.id
        # t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points
        _taskitem = self.taskitemDao.add(t_type, _user.uid, _user.uid, _user.uid, target_mt, target_mt, None, "queue",
                                         tn_id, amount, exchange)
        # 写入t_taskhistory表
        self.taskhistoryDao.add(_taskitem.id, _user.uid, "new", tn_id, "new")
        # self.success(u'操作成功')
        self.success(u'Operation successful.')
        return


# 会计出金(电子钱包出金)
class FinWithdrawHandler(ApiHandler):
    """
    TRIGGER⻚客户出金
    成功触发 客户资变动模块
    失败触发 ⽆
    参数说明
    source_uid 客户id
    target_uid 这里等于上者
    amount 出金金额(USD)
    exchange 出金汇率
    成功触发模块需要根据source_uid账号在t_fundflow表里新建一条debit=amount, type=21的记录
    """

    def post(self):
        amount = self.get_json_argument('amount', default=None)  # 出金金额
        exchange = self.get_json_argument('exchange', default=None)  # 出金汇率

        if not amount:
            # self.error(u'请输入出金金额')
            self.error(u'Please enter the withdraw amount.')
            return
        if not exchange:
            # self.error(u'请输入出金汇率')
            self.error(u'Please enter the exchange rate')
            return
        _user = self.current_user
        if _user.statusa == '封禁' or _user.statusa == '删除':
            # self.err(905, u'该用户状态异常')
            self.err(905, u'Operation is forbidden.')
            return
        # if _user.statusa == '出金冻结' or _user.statusa == '资金冻结':
        if _user.statusa == '出金冻结' or _user.statusa == '审核中':
            # self.err(903, u'该用户状态异常')
            self.err(903, u'User status is abnormal.')
            return
        # 写入t_taskitem表
        _task = self.taskDao.select_by_trigger("/fin/withdraw")
        if not _task:
            # self.error(u'操作失败')
            self.error(u'Operation failed')
            return
        t_type = _task.type
        _tasknode = self.tasknodeDao.select_by_type_step(t_type, 1)
        if not _tasknode:
            # self.error(u'操作失败')
            self.error(u'Operation failed.')
            return
        amount = self.fundflowDao.select_balance(_user.uid)
        if not amount or amount < 0:
            # self.error(u'账户余额不足')
            self.error(u'Insufficient account balance.')
            return
        tn_id = _tasknode.id
        # t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points
        _taskitem = self.taskitemDao.add(t_type, _user.uid, _user.uid, _user.uid, "", "", None, "queue", tn_id,
                                         amount, exchange)
        # 写入t_taskhistory表
        self.taskhistoryDao.add(_taskitem.id, _user.uid, "new", tn_id, "new")

        try:
            vti = self.vtaskitemDao.select_by_id(_taskitem.id)
            amount = self.fundflowDao.select_balance(vti.source_uid)
            if not amount or amount < 0:
                # self.error(u'账户余额不足')
                self.error(u'Insufficient account balance.')
                return
            logger.error("FinWithdraw taskitem_id=%s", _taskitem.id)
            # uid, _type, mtlogin, transaction, extorder, comment, extpay_id, exchange, credit=0, debit=0
            self.fundflowDao.add(vti.source_uid, 21, vti.sourcemt, "", "", "", "", vti.exchange, credit=0,
                                 debit=vti.amount)
            # self.success(u'操作成功')
            self.success(u'Operation successful.')
        except Exception as ex:
            logging.error(ex)
            # self.error(u'操作失败')
            self.error(u'Operation failed.')
        return


# 出金状态跟踪
class FinWithdrawTraceHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument('page', default=None)

        o_uid = self.current_user.uid
        pg = self.vtaskitemDao.select_by_time(o_uid, parser_date(start, "%Y-%m-%d"), parser_date(end, "%Y-%m-%d"), page)
        _objs = []
        for obj in pg.items:
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
        self.suc({"page": page, "total": pg.total, "pages": pg.pages, "list": _objs})
        return


# 出金状态跟踪导出csv(未应用)
class FinWithdrawTraceExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)

        o_uid = self.current_user.uid
        items = self.vtaskitemDao.select_by_time(o_uid, parser_date(start, "%Y-%m-%d"), parser_date(end, "%Y-%m-%d"),
                                                 -1)
        _titles = ["id", "subject", "taskname", "body", "o_uid", "o_cname", "source_uid", "source_cname", "target_uid",
                   "target_cname", "sourcemt", "targetmt", "mtgroup", "amount", "exchange",
                   "points", "state", "tasknode_id", "createtime", "updatetime", "nodename", "step", "approve",
                   "returned", "canapprove", "canreturn", "canreject", "role_id"]
        try:
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            self.write(','.join(_titles) + '\r\n')
            for obj in items:
                self.write(
                    ','.join(
                        [str(obj.id), str(obj.type), str(obj.taskname), str(obj.body), str(obj.o_uid), str(obj.o_cname),
                         str(obj.source_uid), str(obj.source_cname), str(obj.target_uid), str(obj.target_cname),
                         str(obj.sourcemt), str(obj.targetmt), str(obj.mtgroup), "{:.6f}".format(obj.amount),
                         "{:.6f}".format(obj.exchange), str(obj.points), str(obj.state), str(obj.tasknode_id),
                         format_date(obj.createtime), format_date(obj.updatetime), str(obj.nodename), str(obj.step),
                         str(obj.approve), str(obj.returned), str(obj.canapprove), str(obj.canreturn),
                         str(obj.canreject), str(obj.role_id)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 财务操作历史(出入金记录)
class FinHistoryHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        opttype = self.get_json_argument('opttype', default=None)
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument('page', default=None)

        _user = self.current_user
        pagination = self.fundflowDao.select_by_params_page(_user.uid, mtlogin, opttype, parser_date(start, "%Y-%m-%d"),
                                                            parser_date(end, "%Y-%m-%d"), page)
        fundtypes = self.fundtypeDao.select_all()
        fundtypemap = {}
        for ft in fundtypes:
            fundtypemap[ft.type] = ft.name
        fundtypemap2 = {}
        for ft in fundtypes:
            fundtypemap2[ft.type] = ft.ename

        _objs = []
        for obj in pagination.items:
            _objs.append(
                {"id": str(obj.id), "type": obj.type, "typename": fundtypemap[obj.type],
                 "typeename": fundtypemap2[obj.type], "mtlogin": str(obj.mtlogin),
                 "transaction": obj.transaction, "credit": "{:.6f}".format(obj.credit), "comment": obj.comment,
                 "extpay_id": obj.extpay_id, "extorder": obj.extorder, "createtime": format_date(obj.createtime)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 交易账户总览
class FinSummaryHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        page = self.get_json_argument('page', default=None)
        self.suc()
        return


# 交易账户资金变动记录导出csv
class FinHistoryExportHandler(ApiHandler):
    def post(self):
        mtlogin = self.get_json_argument('mtlogin', default=None)
        page = self.get_json_argument('page', default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        # uid = self.get_json_argument('uid', default=None)
        uid = self.current_user.uid
        items = self.fundflowDao.select_by_params_page(uid, mtlogin, None, None, None, -1)
        logger.info('items:[%s]', items)
        fundtypes = self.fundtypeDao.select_all()
        fundtypemap = {}
        fundtypemap2 = {}
        for ft in fundtypes:
            fundtypemap[ft.type] = ft.name
            fundtypemap2[ft.type] = ft.ename
        if version == "international":
            _titles = ["type", "typename", "typeename", "MT login", "transaction", "credit", "comment", "extpay_id",
                       "extorder", "createtime"]
        else:
            _titles = ["类型", "类型中文名", "类型英文名", "MT账户", "交易号", "借", "备注", "支付源", "第三方单号", "创建时间"]
        try:
            self.set_header('Content-Type', 'application/octet-stream')  # 询问"打开”还是“保存"
            self.set_header('Content-Disposition', 'attachment; filename=inner-user.csv; charset=utf-8')
            # 需要提示用户保存，就要利用Content-Disposition进行一下处理，关键在于一定要加上attachment
            self.write(','.join(_titles) + '\r\n')
            for obj in items:
                # st = ",".join(['a','b','c',None,'d'])不能拼接,postgresql里的Null转换成str是存在带空格或不带空格字符串
                self.write(
                    ','.join([str(obj.type), str(fundtypemap[obj.type]), str(fundtypemap2[obj.type]),
                              str(obj.mtlogin), str(obj.transaction),
                              str("{:.6f}".format(obj.credit)), str(obj.comment), str(obj.extpay_id), str(obj.extorder),
                              format_date(obj.createtime)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 电子钱包余额
class BalanceEwalletHandler(ApiHandler):
    def get(self):
        _user = self.current_user
        amount = self.fundflowDao.select_balance(_user.uid)
        self.suc({"amount": "{:.6f}".format(amount)})
        return


# MT交易账户余额
class BalanceMTHandler(ApiHandler):
    def get(self):
        _user = self.current_user
        _mtusers = self.vmtuserDao.select_by_uid(_user.uid)
        _mt = []
        for mtuser in _mtusers:
            _mt.append({"mtlogin": str(mtuser.mtlogin), "balance": "{:.6f}".format(mtuser.balance),
                        "equity": "{:.6f}".format(mtuser.equity)})
        self.suc({"mt": _mt})
        return


# 直客——MT账户成交历史记录
class DealhistoryHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument("page", default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        uid = self.current_user.uid
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


# 直客——MT账户交易历史记录
class TradehistoryHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument("page", default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        uid = self.current_user.uid
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


# 直客——MT账户飘单记录
class OpenpositionHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument("page", default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        uid = self.current_user.uid
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


# 直客——MT账户成交历史导出
class DealhistoryExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        page = -1
        uid = self.current_user.uid

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


# 直客——MT账户交易历史导出
class TradehistoryExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        page = -1
        uid = self.current_user.uid

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
                         "飘单号", "平仓时间", "平仓交易号", "平仓交易量", "平仓价", "利润", "库存费",
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


# 直客——MT账户飘单导出
class OpenpositionExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        page = -1
        uid = self.current_user.uid

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


handlers = [
    (r"/mt/group", GrouptypeHandler),
    (r"/mt/create", MTAddHandler),
    (r"/mt/up", MTUpHandler),
    (r"/mt/pass/up", MTPassUpHandler),
    (r"/mt/record", MTRecordHandler),  # vdealclosed平仓
    (r"/mt/info", MTInfoHandler),
    (r"/mt/dealhistory/record", DealhistoryHandler),
    (r"/mt/tradehistory/record", TradehistoryHandler),
    (r"/mt/openposition/record", OpenpositionHandler),
    (r"/mt/dealhistory/export", DealhistoryExportHandler),
    (r"/mt/tradehistory/export", TradehistoryExportHandler),
    (r"/mt/openposition/export", OpenpositionExportHandler),

    (r"/fin/fundtype", FundtypeHandler),
    (r"/fin/balance/ewallet", BalanceEwalletHandler),
    (r"/fin/balance/mt", BalanceMTHandler),
    (r"/fin/leverage", LeverageHandler),
    (r"/fin/exchange", ExchangeHandler),
    (r"/fin/deposit", FinDepositHandler),
    (r"/fin/pay/status", FinPayStatusHandler),
    (r"/fin/withdraw/mt", FinMTWithdrawHandler),
    (r"/fin/withdraw", FinWithdrawHandler),
    (r"/fin/history", FinHistoryHandler),
    (r"/fin/transfer", FinTransferHandler),
    (r"/fin/history/export", FinHistoryExportHandler),
    (r"/fin/withdraw/trace", FinWithdrawTraceHandler),
    (r"/fin/withdraw/trace/export", FinWithdrawTraceExportHandler),

]
