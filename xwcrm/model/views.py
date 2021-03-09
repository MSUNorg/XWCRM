#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: views.py
@time: 18/8/10 17:33
"""

from models import DBDao, VMtuser, VDealclosed, VFxusdcnh, VCommission, VTaskitem, VClient, Pagination, VDealhistory, \
    VTradehistory, VOpenposition
from sqlalchemy import func
from sqlalchemy import and_, or_
from utils.log_decorator import log_func_parameter

class VMtuserDao(DBDao):
    """
    v_mtuser表操作
    """

    @log_func_parameter
    def select_max_login(self):
        """
        查询最大mtlogin
        :return:MT账户
        """
        res = self.session.query(func.max(VMtuser.mtlogin)).scalar()
        if not res:
            return 0
        return res

    @log_func_parameter
    def select_by_uid(self, uid):
        """
        已知用户id，查询MT账号一览视图
        :param uid:用户id
        :return:MT账号一览视图所有对象
        """
        res = self.session.query(VMtuser.uid, VMtuser.mtlogin, VMtuser.mtgroup, VMtuser.leverage, VMtuser.balance,
                                 VMtuser.marginlevel, VMtuser.equity, VMtuser.type, VMtuser.typename,
                                 VMtuser.groupname, VMtuser.spread, VMtuser.commission, VMtuser.maxbalance).filter(
            VMtuser.uid == uid).all()
        return res

    @log_func_parameter
    def select_by_mtlogin(self, mtlogin):
        """
        已知mtlogin，查询MT账号一览视图
        :param mtlogin: MT账户
        :return: MT账号一览视图所有对象
        """
        res = self.session.query(VMtuser.uid, VMtuser.mtlogin, VMtuser.mtgroup, VMtuser.leverage, VMtuser.balance,
                                 VMtuser.marginlevel, VMtuser.equity, VMtuser.type, VMtuser.typename, VMtuser.groupname,
                                 VMtuser.spread, VMtuser.commission, VMtuser.maxbalance).filter(
            VMtuser.mtlogin == mtlogin).all()
        return res

    @log_func_parameter
    def select_by_uid_first(self, uid):
        """
        已知用户id，查询MT账号一览视图
        :param uid: 用户id
        :return: MT账号一览视图第一个对象
        """
        res = self.session.query(VMtuser.uid, VMtuser.mtlogin, VMtuser.mtgroup, VMtuser.leverage, VMtuser.balance,
                                 VMtuser.marginlevel, VMtuser.equity, VMtuser.type, VMtuser.typename,
                                 VMtuser.groupname, VMtuser.spread, VMtuser.commission, VMtuser.maxbalance).filter(
            VMtuser.uid == uid).first()
        return res

    @log_func_parameter
    def select_by_uid_mtlogin(self, uid, mtlogin):
        """
        这么写没问题？
        已知用户id，MT账号，查询MT账号一览视图
        :param uid: 用户id
        :param mtlogin: MT账户
        :return: MT账号一览视图第一个对象
        """
        query = self.session.query(VMtuser.uid, VMtuser.mtlogin, VMtuser.mtgroup, VMtuser.leverage, VMtuser.balance,
                                   VMtuser.marginlevel, VMtuser.equity, VMtuser.type, VMtuser.typename,
                                   VMtuser.groupname, VMtuser.spread, VMtuser.commission, VMtuser.maxbalance)
        query = query.filter(VMtuser.uid == uid)
        query = query.filter(VMtuser.mtlogin == mtlogin)
        res = query.first()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有MT账号一览视图
        :return: MT账号一览视图对象
        """
        res = self.session.query(VMtuser).all()
        return res


class VDealclosedDao(DBDao):
    """
    v_dealclosed表操作
    """

    @log_func_parameter
    def select_login_symbol(self, login, symbol, start, end, page):
        """
        已知login、symbol，查询MT已平仓单视图
        :param login: 账户
        :param symbol: 品种
        :param start: 开始时间
        :param end: 结束时间
        :param page: 分页
        :return: MT已平仓单视图对象
        """
        query = self.session.query(VDealclosed.deal, VDealclosed.timestamp, VDealclosed.login, VDealclosed.order,
                                   VDealclosed.action, VDealclosed.entry, VDealclosed.reason, VDealclosed.time,
                                   VDealclosed.symbol, VDealclosed.price, VDealclosed.volume, VDealclosed.profit,
                                   VDealclosed.storage, VDealclosed.commission, VDealclosed.rateprofit,
                                   VDealclosed.positionid, VDealclosed.priceposition, VDealclosed.volumeclosed)

        query = query.filter(and_(VDealclosed.login == login, VDealclosed.symbol == symbol))
        if not page or page == '' or page == 'undefined':
            page = 1
        if start and start != '' and start != 'undefined':
            query = query.filter(VDealclosed.timestamp >= start)
        if end and end != '' and end != 'undefined':
            query = query.filter(VDealclosed.timestamp <= end)
        query.order_by(VDealclosed.timestamp)
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_login_agentid(self, login, agent_id, start, end, page):
        """
        已知login、agent_id，查询MT已平仓单视图
        :param login: 账户
        :param agent_id: 代理id
        :param start: 开始时间
        :param end: 结束时间
        :param page: 分页
        :return: MT已平仓单视图对象
        """
        query = self.session.query(VDealclosed.deal, VDealclosed.timestamp, VDealclosed.login, VDealclosed.order,
                                   VDealclosed.action, VDealclosed.entry, VDealclosed.reason, VDealclosed.time,
                                   VDealclosed.symbol, VDealclosed.price, VDealclosed.volume, VDealclosed.profit,
                                   VDealclosed.storage, VDealclosed.commission, VDealclosed.rateprofit,
                                   VDealclosed.positionid, VDealclosed.priceposition, VDealclosed.volumeclosed)

        query.filter(VDealclosed.login == login)
        if not page or page == '' or page == 'undefined':
            page = 1
        if start and start != '' and start != 'undefined':
            query = query.filter(VDealclosed.timestamp >= start)
        if agent_id and agent_id != '' and agent_id != 'undefined':
            query = query.filter(VDealclosed.agent_id1 == agent_id)
        if end and end != '' and end != 'undefined':
            query = query.filter(VDealclosed.timestamp <= end)
        query.order_by(VDealclosed.timestamp)
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_all(self):
        """
        查询所有MT已平仓单视图
        :return: 所有MT已平仓单视图
        """
        res = self.session.query(VDealclosed).all()
        return res


class VFxusdcnhDao(DBDao):
    """
    v_fxusdcnh表操作
    """

    @log_func_parameter
    def select_exchange(self):
        """
        查询人民币汇率视图
        :return: 人民币汇率视图第一个对象
        """
        res = self.session.query(VFxusdcnh.depositfx, VFxusdcnh.withdrawfx).first()
        return res

    @log_func_parameter
    def select_all(self):
        """
        查询所有人民币汇率视图
        :return: 所有人民币汇率视图
        """
        res = self.session.query(VFxusdcnh).all()
        return res


class VCommissionDao(DBDao):
    """
    v_commission表操作
    """

    @log_func_parameter
    def select_page(self, cname, mobile, email, mtlogin, agent_id, page):
        """
        已知cname, mobile, email, mtlogin, agent_id，查询人民币汇率视图
        :param cname: 姓名
        :param mobile: ⼿机号
        :param email: 电⼦邮箱
        :param mtlogin: MT账户
        :param agent_id: 上级代理
        :param page: 分页
        :return:人民币汇率视图
        """
        query = self.session.query(VCommission.uid, VCommission.mobile, VCommission.agent_id, VCommission.cname,
                                   VCommission.email, VCommission.mtlogin, VCommission.spread, VCommission.commission,
                                   VCommission.agent_id1, VCommission.reward1, VCommission.agent_id2,
                                   VCommission.reward2, VCommission.agent_id3, VCommission.reward3)

        if agent_id and agent_id != '' and agent_id != 'undefined':
            query = query.filter(VCommission.agent_id == agent_id)
        if cname and cname != '' and cname != 'undefined':
            query = query.filter(VCommission.cname == cname)
        if mobile and mobile != '' and mobile != 'undefined':
            query = query.filter(VCommission.mobile == mobile)
        if email and email != '' and email != 'undefined':
            query = query.filter(VCommission.email == email)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(VCommission.mtlogin == mtlogin)
        query.order_by(VCommission.uid)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)


class VTaskitemDao(DBDao):
    """
    v_taskitem表操作
    """

    @log_func_parameter
    def select_taskname(self):
        """
        查询taskname（不重复）
        :return:taskname
        """
        res = self.session.query(VTaskitem.taskname).distinct(VTaskitem.taskname).all()
        return res

    @log_func_parameter
    def select_page(self, task_type, o_uid, state, o_cname, role_ids, page=None):
        '''
        已知task_type, o_uid, state, o_cname, role_ids,查看任务一览视图
        :param task_type: taskname任务名称
        :param o_uid: 发起⼈
        :param state: 状态
        :param o_cname: 发起⼈姓名
        :param role_ids: 处理者role
        :param page: 分页
        :return: 任务一览视图对象
        '''
        query = self.session.query(VTaskitem.id, VTaskitem.subject, VTaskitem.taskname, VTaskitem.body, VTaskitem.o_uid,
                                   VTaskitem.o_cname, VTaskitem.source_uid, VTaskitem.source_cname,
                                   VTaskitem.target_uid, VTaskitem.target_cname, VTaskitem.sourcemt, VTaskitem.targetmt,
                                   VTaskitem.mtgroup, VTaskitem.amount, VTaskitem.exchange, VTaskitem.points,
                                   VTaskitem.state, VTaskitem.tasknode_id, VTaskitem.createtime, VTaskitem.updatetime,
                                   VTaskitem.nodename, VTaskitem.step, VTaskitem.approve, VTaskitem.returned,
                                   VTaskitem.canapprove, VTaskitem.canreturn, VTaskitem.canreject, VTaskitem.role_id)

        if task_type and task_type != '' and task_type != 'undefined':
            query = query.filter(VTaskitem.taskname == task_type)
        if state and state != '' and state != 'undefined' and state > 0:
            query = query.filter(VTaskitem.state == state)
        if state == -1:
            query = query.filter(or_(VTaskitem.state == "queue", VTaskitem.state == "returned"))
        if state == -2:
            query = query.filter(or_(VTaskitem.state == "finished", VTaskitem.state == "reject"))
        if o_uid and o_uid != '' and o_uid != 'undefined':
            query = query.filter(VTaskitem.o_uid == o_uid)
        if o_cname and o_cname != '' and o_cname != 'undefined':
            query = query.filter(VTaskitem.o_cname == o_cname)
        if role_ids and role_ids != '' and role_ids != 'undefined':
            query = query.filter(VTaskitem.role_id.in_(role_ids))
        query.order_by(VTaskitem.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_by_time(self, o_uid, start, end, page=None):
        """
        已知 o_uid, 查看任务一览视图
        :param o_uid: 发起⼈
        :param start: 开始时间
        :param end: 结束时间
        :param page: 分页
        :return: 任务一览视图对象
        """
        query = self.session.query(VTaskitem.id, VTaskitem.subject, VTaskitem.taskname, VTaskitem.body, VTaskitem.o_uid,
                                   VTaskitem.o_cname, VTaskitem.source_uid, VTaskitem.source_cname,
                                   VTaskitem.target_uid, VTaskitem.target_cname, VTaskitem.sourcemt, VTaskitem.targetmt,
                                   VTaskitem.mtgroup, VTaskitem.amount, VTaskitem.exchange, VTaskitem.points,
                                   VTaskitem.state, VTaskitem.tasknode_id, VTaskitem.createtime, VTaskitem.updatetime,
                                   VTaskitem.nodename, VTaskitem.step, VTaskitem.approve, VTaskitem.returned,
                                   VTaskitem.canapprove, VTaskitem.canreturn, VTaskitem.canreject, VTaskitem.role_id)
        if o_uid and o_uid != '' and o_uid != 'undefined':
            query = query.filter(VTaskitem.o_uid == o_uid)
        if start and start != '' and start != 'undefined':
            query = query.filter(VTaskitem.createtime >= start)
        if end and end != '' and end != 'undefined':
            query = query.filter(VTaskitem.createtime <= end)
        query.order_by(VTaskitem.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_by_id(self, taskitem_id):
        """
        已知taskitem_id，查看任务一览视图
        :param taskitem_id:任务条款id
        :return:任务一览视图对象
        """
        query = self.session.query(VTaskitem.id, VTaskitem.subject, VTaskitem.taskname, VTaskitem.body, VTaskitem.o_uid,
                                   VTaskitem.o_cname, VTaskitem.source_uid, VTaskitem.source_cname,
                                   VTaskitem.target_uid, VTaskitem.target_cname, VTaskitem.sourcemt, VTaskitem.targetmt,
                                   VTaskitem.mtgroup, VTaskitem.amount, VTaskitem.exchange, VTaskitem.points,
                                   VTaskitem.state, VTaskitem.tasknode_id, VTaskitem.createtime, VTaskitem.updatetime,
                                   VTaskitem.nodename, VTaskitem.step, VTaskitem.approve, VTaskitem.returned,
                                   VTaskitem.canapprove, VTaskitem.canreturn, VTaskitem.canreject, VTaskitem.role_id,
                                   VTaskitem.success, VTaskitem.fail)
        query = query.filter(VTaskitem.id == taskitem_id)
        query.order_by(VTaskitem.createtime)
        return query.first()


class VClientDao(DBDao):
    """
    # 外部客户查询接口
    v_client表操作
    """

    @log_func_parameter
    def search_page_join(self, cname, mobile, email, certid, mtlogin, agent_id, agent, bankaccount, page=None):
        """
        已知cname, mobile, email, certid, mtlogin, agent_id, bankaccount,查询客户视图
        :param cname: 中文姓名
        :param mobile: 手机号
        :param email: 电子邮箱
        :param certid: 证件号
        :param mtlogin: MT账户
        :param agent_id: 代理商编码
        :param bankaccount: 银行账户
        :param page: 分页
        :return: 客户视图对象
        """
        query = self.session.query(VClient.uid, VClient.cname, VClient.mobile, VClient.email, VClient.certid,
                                   VClient.bankaccount, VClient.mtlogin, VClient.statusa, VClient.agent,
                                   VClient.agentid, VClient.a_createtime, VClient.parentid, VClient.a_level,
                                   VClient.a_status, VClient.createtime)
        if cname and cname != '' and cname != 'undefined':
            query = query.filter(VClient.cname.like('%' + cname + '%'))
        if mobile and mobile != '' and mobile != 'undefined':
            query = query.filter(VClient.mobile == mobile)
        if email and email != '' and email != 'undefined':
            query = query.filter(VClient.email == email)
        if certid and certid != '' and certid != 'undefined':
            query = query.filter(VClient.certid == certid)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(VClient.mtlogin.any(str(mtlogin)))#VClient.mtlogin中任何一项与str(mtlogin)相等
            # query = query.filter(VClient.mtlogin.contains(str(mtlogin)))
        if agent_id and agent_id != '' and agent_id != 'undefined':
            query = query.filter(VClient.agentid == agent_id)
        if agent and agent != '' and agent != 'undefined':
            query = query.filter(VClient.agent == agent)
        if bankaccount and bankaccount != '' and bankaccount != 'undefined':
            query = query.filter(VClient.bankaccount == bankaccount)
        query.order_by(VClient.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)


class VDealhistoryDao(DBDao):
    """
    v_dealhistory视图操作
    """

    @log_func_parameter
    def search_by_uid(self, uid, start, end, mtlogin, page=None):
        """
        已知id，根据时间段，查询已成交订单
        :param uid:用户id
        :param start:起始时间
        :param end:结束时间
        :param page:请求页
        :return:queryset
        """
        query = self.session.query(VDealhistory.time, VDealhistory.deal, VDealhistory.positionid, VDealhistory.login,
                                   VDealhistory.symbol, VDealhistory.action, VDealhistory.entry, VDealhistory.volume,
                                   VDealhistory.price, VDealhistory.priceposition, VDealhistory.profit,
                                   VDealhistory.storage, VDealhistory.commission, VDealhistory.profitraw).filter(
            VDealhistory.uid == uid)
        if start and start != '' and start != 'undefined':
            query = query.filter(VDealhistory.time >= start)
        if end and end != '' and end != 'undefined':
            query = query.filter(VDealhistory.time <= end)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(VDealhistory.login == mtlogin)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def searchsum_by_uid(self, uid, start, end, mtlogin):
        """
        已知用户id，根据时间段，查询总和
        :param uid: 用户id
        :param start: 开始时间
        :param end: 结束时间
        :return: 各项总和
        """
        query = self.session.query(VDealhistory.time, VDealhistory.login, VDealhistory.profit, VDealhistory.storage,
                                   VDealhistory.commission,
                                   VDealhistory.profitraw).filter(
            VDealhistory.uid == uid)
        sum_list = []
        profit_sum = 0  # 利润总和
        storage_sum = 0  # 库存费总和
        commission_sum = 0  # 手续费总和
        profitraw_sum = 0  # 净利润总和

        if start and start != '' and start != 'undefined':
            query = query.filter(VDealhistory.time >= start)
        if end and end != '' and end != 'undefined':
            query = query.filter(VDealhistory.time <= end)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(VDealhistory.login == mtlogin)
        for obj in query:
            profit_sum = profit_sum + obj.profit
            storage_sum = storage_sum + obj.storage
            commission_sum = commission_sum + obj.commission
            profitraw_sum = profitraw_sum + obj.profitraw
        sum_list.append(
            {"profit_sum": str(profit_sum), "storage_sum": str(storage_sum), "commission_sum": str(commission_sum),
             "profitraw_sum": str(profitraw_sum)})
        # query = query.query(func.sum(VDealhistory.profit),func.sum(VDealhistory.storage),func.sum(VDealhistory.commission),func.sum(VDealhistory.profitraw))
        return sum_list


class VTradehistoryDao(DBDao):
    """
    v_tradehistory视图操作
    """

    @log_func_parameter
    def search_by_uid(self, uid, start, end, mtlogin, page=None):
        """
        已知用户id，根据时间段，查询交易订单
        :param uid:用户id
        :param start:起始时间
        :param end:结束时间
        :param page:请求页
        :return:queryset
        """
        query = self.session.query(VTradehistory.o_time, VTradehistory.o_deal, VTradehistory.login,
                                   VTradehistory.symbol,
                                   VTradehistory.o_action, VTradehistory.volume, VTradehistory.o_price,
                                   VTradehistory.o_commission, VTradehistory.positionid, VTradehistory.c_time,
                                   VTradehistory.c_deal, VTradehistory.volumeclosed, VTradehistory.c_price,
                                   VTradehistory.profit, VTradehistory.storage, VTradehistory.c_commission,
                                   VTradehistory.profitraw).filter(
            VTradehistory.uid == uid)
        if start and start != '' and start != 'undefined':
            query = query.filter(VTradehistory.o_time >= start)
        if end and end != '' and end != 'undefined':
            query = query.filter(VTradehistory.o_time <= end)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(VTradehistory.login == mtlogin)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def searchsum_by_uid(self, uid, start, end, mtlogin):
        """
        已知用户id，根据时间段，查询总和
        :param uid: 用户id
        :param start: 开始时间
        :param end: 结束时间
        :return: 各项总和
        """
        query = self.session.query(VTradehistory.o_time, VTradehistory.login, VTradehistory.profit,
                                   VTradehistory.storage, VTradehistory.c_commission,
                                   VTradehistory.profitraw).filter(
            VTradehistory.uid == uid)

        if start and start != '' and start != 'undefined':
            query = query.filter(VTradehistory.o_time >= start)
        if end and end != '' and end != 'undefined':
            query = query.filter(VTradehistory.o_time <= end)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(VTradehistory.login == mtlogin)
        sum_list = []
        profit_sum = 0  # 利润总和
        storage_sum = 0  # 库存费总和
        c_commission_sum = 0  # 手续费总和
        profitraw_sum = 0  # 净利润总和

        for obj in query:
            profit_sum = profit_sum + obj.profit
            storage_sum = storage_sum + obj.storage
            c_commission_sum = c_commission_sum + obj.c_commission
            profitraw_sum = profitraw_sum + obj.profitraw
        sum_list.append(
            {"profit_sum": str(profit_sum), "storage_sum": str(storage_sum), "c_commission_sum": str(c_commission_sum),
             "profitraw_sum": str(profitraw_sum)})
        # query = query.query(func.sum(VDealhistory.profit),func.sum(VDealhistory.storage),func.sum(VDealhistory.commission),func.sum(VDealhistory.profitraw))
        return sum_list


class VOpenpositionDao(DBDao):
    """
    v_openposition视图操作
    """

    @log_func_parameter
    def search_by_uid(self, uid, start, end, mtlogin, page=None):
        """
        已知用户id，根据时间段，查询飘单记录
        :param uid: 用户id
        :param start: 开始时间
        :param end: 结束时间
        :return: 各项总和
        """
        query = self.session.query(VOpenposition.timecreate, VOpenposition.timeupdate, VOpenposition.position,
                                   VOpenposition.login, VOpenposition.symbol, VOpenposition.action,
                                   VOpenposition.volume, VOpenposition.priceopen, VOpenposition.pricesl,
                                   VOpenposition.pricetp, VOpenposition.pricecurrent, VOpenposition.storage,
                                   VOpenposition.profit).filter(
            VOpenposition.uid == uid)

        if start and start != '' and start != 'undefined':
            query = query.filter(VOpenposition.timecreate >= start)
        if end and end != '' and end != 'undefined':
            query = query.filter(VOpenposition.timecreate <= end)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(VOpenposition.login == mtlogin)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def searchsum_by_uid(self, uid, start, end, mtlogin):
        """
        已知用户id，根据时间段，查询总和
        :param uid: 用户id
        :param start: 开始时间
        :param end: 结束时间
        :return: 各项总和
        """
        query = self.session.query(VOpenposition.timecreate, VOpenposition.login, VOpenposition.profit,
                                   VOpenposition.storage).filter(
            VOpenposition.uid == uid)

        if start and start != '' and start != 'undefined':
            query = query.filter(VOpenposition.timecreate >= start)
        if end and end != '' and end != 'undefined':
            query = query.filter(VOpenposition.timecreate <= end)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(VOpenposition.login == mtlogin)
        sum_list = []
        profit_sum = 0  # 利润总和
        storage_sum = 0  # 库存费总和
        for obj in query:
            profit_sum = profit_sum + obj.profit
            storage_sum = storage_sum + obj.storage
        sum_list.append(
            {"profit_sum": str(profit_sum), "storage_sum": str(storage_sum)})
        return sum_list
