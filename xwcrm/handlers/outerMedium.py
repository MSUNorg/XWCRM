#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: outerMedium.py
@time: 18/6/15 15:12
@description: 外部中间人操作
"""

from base import *
from utils.utils import parser_date, format_date

logger = logging.getLogger('xwcrm.outerMedium')


# 搜索客户
class CustomerSearchHandler(ApiHandler):
    def post(self):
        cname = self.get_json_argument('cname', default=None)
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        page = self.get_json_argument('page', default=None)

        _user = self.current_user
        _agent = self.agentDao.select_by_uid(_user.uid)
        if not _agent:
            self.error("agent is null")
            return
        agent_id = _agent.agentid
        pagination = self.vcommissionDao.select_page(cname, mobile, email, mtlogin, agent_id, page)
        _objs = []
        for obj in pagination.items:
            _objs.append(
                {"uid": obj.uid, "cname": obj.cname, "mobile": obj.mobile, "email": obj.email, "agent_id": obj.agent_id,
                 "mtlogin": str(obj.mtlogin), "spread": str(obj.spread), "commission": str(obj.commission),
                 "agent_id1": obj.agent_id1, "reward1": str(obj.reward1), "agent_id2": obj.agent_id2,
                 "reward2": str(obj.reward2), "agent_id3": obj.agent_id3, "reward3": str(obj.reward3)})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 代理商——导出客户csv
class CustomerExportHandler(ApiHandler):
    def post(self):
        cname = self.get_json_argument('cname', default=None)
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        version = self.get_json_argument('version', default=None)#国际版
        page = -1
        uid = self.current_user.uid
        _agent = self.agentDao.select_by_uid(uid)
        if not _agent:
            self.error("export csv file fail")
            return
        agent_id = _agent.agentid
        try:
            items = self.vcommissionDao.select_page(cname, mobile, email, mtlogin, agent_id, page)
            if not items:
                self.error(u'没有可导出的数据')
                return
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=customer.csv; charset=utf-8')
            if version == "international":
                self.write(','.join(["Name", "Mobile", "Email", "Agent", "MT login", "Spread", "Commission"]) + '\r\n')
            else:
                self.write(','.join(["姓名", "电话", "邮箱", "代理", "MT账户", "内佣", "外佣"]) + '\r\n')
            for obj in items:
                self.write(','.join([str(obj.cname), str(obj.mobile), str(obj.email), str(obj.agent_id),
                                     str(obj.mtlogin), str(obj.spread), str(obj.commission)]) + '\r\n')
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("export csv file fail")
            return


# 升级名下客户
class UpgradeCustomerHandler(ApiHandler):
    def post(self):
        source_uid = self.get_json_argument('source_uid', default=None)
        cname = self.get_json_argument('cname', default=None)
        points = self.get_json_argument('points', default=None)

        if not source_uid:
            self.error(u'请输入用户ID')
            return
        if not cname:
            self.error(u'请输入用户名称')
            return
        if not points:
            self.error(u'请输入新佣金')
            return

        _user = self.current_user
        # 写入t_taskitem表
        _task = self.taskDao.select_by_trigger("/medium/upgrade")
        if not _task:
            self.error(u'操作失败')
            return
        t_type = _task.type
        _tasknode = self.tasknodeDao.select_by_type_step(t_type, 1)
        if not _tasknode:
            self.error(u'操作失败')
            return
        tn_id = _tasknode.id
        # t_type, o_uid, source_uid, target_uid, sourcemt, targetmt, mtgroup, state, tasknode_id, amount, exchange, points
        _taskitem = self.taskitemDao.add(t_type, _user.uid, source_uid, _user.uid, "", "", None, "queue",
                                         tn_id, 0, 0, points)
        # 写入t_taskhistory表
        self.taskhistoryDao.add(_taskitem.id, _user.uid, "new", tn_id, "new")
        self.success(u'操作成功')
        return


# 修改交易佣金
class UpdateBrokerageHandler(ApiHandler):
    def post(self):
        source_uid = self.get_json_argument('source_uid', default=None)
        cname = self.get_json_argument('cname', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        spread = self.get_json_argument('spread', default=None)
        commission = self.get_json_argument('commission', default=None)

        if not source_uid:
            self.error(u'请输入用户ID')
            return
        if not cname:
            self.error(u'请输入用户名称')
            return
        if not mtlogin:
            self.error(u'请输入MT账号')
            return
        if not spread:
            self.error(u'请输入内佣加点')
            return
        if not commission:
            self.error(u'请输入外佣加点')
            return

        _mtuser = self.vmtuserDao.select_by_uid_mtlogin(source_uid, mtlogin)
        if not _mtuser:
            self.error(u'用户错误')
            return
        old_type = _mtuser.type
        old_leverage = _mtuser.leverage
        logging.error("old_leverage:", str(old_leverage))
        """
        mtgroup = select mtname from t_mtgroup where type=old_type
                 and leverage=old_leverage
                 and spread=new_spread
                 and commission=new_commission
        mtgroup为空则目标组合不存在
        old_type=1, new_spread=0, new_commission=0, old_leverage=100
        """
        mtname = self.mtgroupDao.select_mtname(old_type=old_type, new_spread=spread, new_commission=commission,
                                               old_leverage=old_leverage)
        logging.error("mtname:", str(mtname))
        if not mtname:
            self.error(u'您选择的佣金组合不存在')
            return
        try:
            isSuc = self.mtDao.doGroup(str(mtlogin), str(old_leverage), mtname)
            if isSuc:
                self.success(u'操作成功')
                return
        except Exception as ex:
            logging.error(ex)
        self.error(u'操作失败')
        return


# 修改代理返佣
class UpdateMediumHandler(ApiHandler):
    def post(self):
        source_uid = self.get_json_argument('source_uid', default=None)
        cname = self.get_json_argument('cname', default=None)
        points = self.get_json_argument('points', default=None)

        if not source_uid:
            self.error(u'请输入用户ID')
            return
        if not cname:
            self.error(u'请输入用户名称')
            return
        if not points:
            self.error(u'请输入新佣金')
            return

        _agent = self.agentDao.select_by_uid(source_uid)
        if not _agent:
            self.error(u'代理商错误')
            return
        self.agentDao.update(_agent.agentid, {"reward": points})
        self.success(u'操作成功')
        return


# 代理商查看财务操作历史
class FinHistoryHandler(ApiHandler):
    def post(self):
        source_uid = self.get_json_argument('source_uid', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        opttype = self.get_json_argument('opttype', default=None)
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument('page', default=None)

        if not source_uid:
            self.error(u'请输入名下客户ID')
            return
        if not mtlogin:
            self.error(u'请输入名下MT账户')
            return
        pagination = self.fundflowDao.select_by_params_page(source_uid, mtlogin, opttype,
                                                            parser_date(start, "%Y-%m-%d"),
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
        self.suc(_objs)
        return


# 代理商查看客户佣金记录
class BrokerageRecordHandler(ApiHandler):
    def post(self):
        agentid = self.get_json_argument('agentid', default=None)
        mtlogin = self.get_json_argument('mtlogin', default=None)
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument('page', default=None)

        if not mtlogin:
            self.error(u'请输入交易账户')
            return
        if not agentid:
            self.error(u'请输入代理商编码')
            return

        pagination = self.vdealclosedDao.select_login_agentid(mtlogin, agentid, parser_date(start, "%Y-%m-%d"),
                                                              parser_date(end, "%Y-%m-%d"), page)
        _objs = []
        for rec in pagination.items:
            _objs.append(
                {"deal": rec.deal, "timestamp": format_date(rec.timestamp), "login": rec.login, "order": rec.order,
                 "action": rec.action, "entry": rec.entry, "reason": rec.reason, "time": format_date(rec.time),
                 "symbol": rec.symbol, "price": rec.price, "volume": rec.volume, "profit": rec.profit,
                 "storage": rec.storage, "commission": rec.commission, "rateprofit": rec.rateprofit,
                 "positionid": rec.positionid, "priceposition": rec.priceposition, "volumeclosed": rec.volumeclosed})
        self.suc({"page": page, "total": pagination.total, "pages": pagination.pages, "list": _objs})
        return


# 查看代理网络
class TreeHandler(ApiHandler):
    def get(self):
        self.success(u'操作成功', None)
        return


# 代理商——MT账户成交历史记录
class DealhistoryHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument("page", default=None)
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        if not uid:
            self.error(u'请输入用户ID')
            return
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


# 代理商——MT账户交易历史记录
class TradehistoryHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument("page", default=None)
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        if not uid:
            self.error(u'请输入用户ID')
            return
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


# 代理商——MT账户飘单记录
class OpenpositionHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        page = self.get_json_argument("page", default=None)
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        if not uid:
            self.error(u'请输入用户ID')
            return
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


# 代理商——MT账户成交历史导出
class DealhistoryExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        if not uid:
            self.error(u'请输入用户ID')
            return
        page = -1

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


# 代理商——MT账户交易历史导出
class TradehistoryExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        if not uid:
            self.error(u'请输入用户ID')
            return
        page = -1

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
                    ",".join(["TimeOpen", "DealOpen", "MT login", "Symbol", "Action", "LotOpen", "PriceOpen", "Comm.Open",
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


# 代理商——MT账户飘单导出
class OpenpositionExportHandler(ApiHandler):
    def post(self):
        start = self.get_json_argument('start', default=None)
        end = self.get_json_argument('end', default=None)
        uid = self.get_json_argument("uid", default=None)
        mtlogin = self.get_json_argument("mtlogin", default=None)
        version = self.get_json_argument('version', default=None)  # 国际版
        if not uid:
            self.error(u'请输入用户ID')
            return
        page = -1

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
    (r"/medium/customer/search", CustomerSearchHandler),
    (r"/medium/customer/export", CustomerExportHandler),
    (r"/medium/upgrade", UpgradeCustomerHandler),
    (r"/medium/update/brokerage", UpdateBrokerageHandler),
    (r"/medium/update/medium", UpdateMediumHandler),
    (r"/medium/fin/history", FinHistoryHandler),
    (r"/medium/record/brokerage", BrokerageRecordHandler),
    (r"/medium/tree", TreeHandler),

    (r"/medium/dealhistory/record", DealhistoryHandler),
    (r"/medium/tradehistory/record", TradehistoryHandler),
    (r"/medium/openposition/record", OpenpositionHandler),
    (r"/medium/dealhistory/export", DealhistoryExportHandler),
    (r"/medium/tradehistory/export", TradehistoryExportHandler),
    (r"/medium/openposition/export", OpenpositionExportHandler),

]
