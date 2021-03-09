#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: task.py
@time: 18/6/20 17:33
"""

import logging

from model import taskitem, taskhistory, tasknode
from model import views, fundflow, agent, user, mt, mtgroup, role
from models import DBDao, TTask, Pagination
from utils.log_decorator import log_func_parameter

logger = logging.getLogger('xwcrm.handler')


class TaskSuccess:
    """
    任务成功
    """

    def __init__(self):
        self.taskDao = TTaskDao()
        self.tasknodeDao = tasknode.TTaskNodeDao()
        self.taskitemDao = taskitem.TTaskItemDao()
        self.vtaskitemDao = views.VTaskitemDao()
        self.fundflowDao = fundflow.TFundflowDao()
        self.taskhistoryDao = taskhistory.TTaskHistoryDao()
        self.agentDao = agent.TAgentDao()
        self.userDao = user.UserDao()
        self.mtDao = mt.MTDao()
        self.mtgroupDao = mtgroup.TMTGroupDao()
        self.roleDao = role.TRoleDao()

    @log_func_parameter
    def MTWithdraw(self, taskitem_id):
        """
        MT出金
        TRIGGER⻚   客户出金
        成功触发     MT出金模块
        失败触发     简单FAIL接口
        参数说明
        source_uid  客户id
        target_uid  这里等于上者
        source_mt   出金MT账号
        target_mt   这里等于上者
        amount      出金金额(USD)
        exchange    出金汇率
        备注
        成功触发模块需要将source_mt账号里的amount金额扣除,MT注释为’XWCRM withdraw’
        成功触发模块需要根据source_uid账号在t_fundflow表里新建一条如下记录: 
        credit=amount, type=20, uid=source_uid, mtlogin=source_mt, exchange=exchange
        成功触发模块将触发一个新的工作流为“会计出金”,o_uid继承自MT出金任务的o_uid
        :return:
        """
        try:
            vti = self.vtaskitemDao.select_by_id(taskitem_id)
            amount = vti.amount
            source_uid = vti.source_uid
            logger.info("MTWithdraw taskitem_id=%s", taskitem_id)
            isbalance = self.mtDao.doBalance(str(vti.sourcemt), str(-amount), "2", comment="XWCRM withdrawal")
            if isbalance:
                self.fundflowDao.add(source_uid, 20, vti.sourcemt, "", "", "", "", vti.exchange, amount, 0)
                # uid, _type, mtlogin, transaction, extorder, comment, extpay_id, exchange, credit=0, debit=0
                self.fundflowDao.add(vti.source_uid, 21, vti.sourcemt, "", "", "", "", vti.exchange, 0, vti.amount)
        except Exception as ex:
            logging.error(ex)
            return '操作失败'
        try:
            # 生成会计出金工作流
            # 写入t_taskitem表
            logger.info("MTWithdraw end and build FinWithdrawHandler taskitem, source_uid=%s", source_uid)
            _task = self.taskDao.select_by_trigger("/fin/withdraw")
            t_type = _task.type
            _tasknode = self.tasknodeDao.select_by_type_step(t_type, 1)
            tn_id = _tasknode.id
            _taskitem = self.taskitemDao.add(t_type, source_uid, source_uid, source_uid, "", "", None, "queue", tn_id,
                                             amount, vti.exchange)
            # 写入t_taskhistory表
            self.taskhistoryDao.add(_taskitem.id, source_uid, "new", tn_id, "new")
            return ''
        except Exception as ex:
            logging.error(ex)
        return '新建任务失败'

    @log_func_parameter
    def FinWithdraw(self, taskitem_id):
        """
        会计出金
        TRIGGER⻚客户出⾦
        成功触发 客户资⾦变动模块
        失败触发 ⽆
        参数说明
        source_uid 客户id
        target_uid 这里等于上者
        amount 出金金额(USD)
        exchange 出金汇率
        备注
        成功触发模块操作：
        前置检查电子钱包余额：
        余额 = select sum(credit) - sum(debit) from t_fundflow where type=10 or type=11 or type=31
        or type=50 or type=51 or type=20 or type=21
        IF 余额 - amount < 0 THEN 任务结束并且报错：“账户余额不足”
        ELSE 在t_fundflow表里新建一条记录：
        {
            uid = source_uid
            debit = amount
            credit = 0
            type = 21
            exchange = exchange
        }
        :return:
        """
        """
        try:
            vti = self.vtaskitemDao.select_by_id(taskitem_id)
            amount = self.fundflowDao.select_balance(vti.source_uid)
            if not amount or amount < 0:
                return u'账户余额不足'
            logger.error("FinWithdraw taskitem_id=%s", taskitem_id)
            # uid, _type, mtlogin, transaction, extorder, comment, extpay_id, exchange, credit=0, debit=0
            self.fundflowDao.add(vti.source_uid, 21, vti.sourcemt, "", "", "", "", vti.exchange, 0, vti.amount)
            return ''
        except Exception as ex:
            logging.error(ex)
        """
        return ''

    @log_func_parameter
    def AgentsCreate(self, taskitem_id):
        """
        新建代理商
        TRIGGER⻚新建代理商
        成功触发 更新MT代理商数据和代理商表模块
        失败触发 简单FAIL
        参数说明
        source_uid 客户id
        target_uid 代理商id，在这里等于上者
        points 返佣点数
        备注
        成功触发模块操作
        在t_agent表里添加一条记录：
        {
            agentid = 自动生成
            uid = source_uid
            reward = points
            level = 1
            status = ‘正常’
        }
        更新t_user表 where uid = source_uid ：
        {
            agent_id = 上面自动生成的agentid
            role_id[2] = select id from t_role where name =‘代理商’
        }
        :return:
        """
        try:
            vti = self.vtaskitemDao.select_by_id(taskitem_id)
            # uid, level, reward, status, parentid
            _agent = self.agentDao.add(vti.source_uid, 1, vti.points, u'正常')
            _role = self.roleDao.select_by_name(u'代理商', 0)
            _role2 = self.roleDao.select_by_name(u'终端客户', 0)
            role_ids = []
            role_ids.append(_role2.id)
            role_ids.append(_role.id)
            self.userDao.update_agent_role(vti.source_uid, _agent.agentid, role_ids)
            return ''
        except Exception as ex:
            logging.error(ex)
        return '操作失败'

    @log_func_parameter
    def AgentsCustomerUpdate(self, taskitem_id):
        """
        修改客户代理
        TRIGGER  修改客户代理
        成功触发 更新MT代理商数据和代理商表模块
        失败触发 简单FAIL接⼝
        参数说明
        source_uid 客户id
        target_uid 代理商id
        备注
        成功触发模块需要根据更新t_user表 where uid = source_uid :
        {  agent_id = (select agentid from t_agent where uid = target_uid) }
        :return:
        """
        try:
            vti = self.vtaskitemDao.select_by_id(taskitem_id)
            _agent = self.agentDao.select_by_uid(vti.target_uid)
            self.userDao.update_agent(vti.source_uid, _agent.agentid)
            return ''
        except Exception as ex:
            logging.error(ex)
        return '操作失败'

    @log_func_parameter
    def UpgradeCustomer(self, taskitem_id):
        """
        代理商升级名下客户
        TRIGGER  代理商升级名下客户
        成功触发 更新MT代理商数据和代理商表模块
        失败触发 简单FAIL接⼝
        参数说明
        source_uid 目标客户id
        target_uid 代理商id
        points 返佣点数
        备注
        任务提交的前置检查
        If (select level from t_agent where uid = target_uid) == 3
        then 提示错误：“代理商资格不符”
        成功触发模块需要根据source_uid在t_agent表里添加一条记录：
        {
            agentid = 自动生成8位
            uid = source_uid
            parentid = (select agentid from t_agent where uid = target_uid)
            reward = points
            level = (select level from t_agent where uid = target_uid) + 1
            status = ‘正常’
        }
        更新t_user表 where uid = source_uid ：
        {
            agent_id = target_uid
            role_id[2] = select id from t_role where name =‘代理商’
        }
        :return:
        """
        try:
            vti = self.vtaskitemDao.select_by_id(taskitem_id)
            source_uid = vti.source_uid
            target_uid = vti.target_uid
            _agent = self.agentDao.select_by_uid(target_uid)
            parentid = _agent.agentid
            if not _agent or _agent.level == 3:
                return '代理商资格不符'
            # uid, level, reward, status, parentid
            _level = _agent.level + 1
            self.agentDao.add(source_uid, _level, vti.points, u'正常', parentid)
            _role = self.roleDao.select_by_name(u'代理商', 0)
            self.userDao.update_agent_role(source_uid, target_uid, _role.id)
            return ''
        except Exception as ex:
            logging.error(ex)
        return '操作失败'

    @log_func_parameter
    def AgentsUpdate(self, taskitem_id):
        """
        修改代理商
        TRIGGER⻚   修改代理商
        成功触发     更新MT代理商数据和代理商表模块
        失败触发     简单FAIL
        参数说明
        source_uid  代理商id
        target_uid  上级代理id
        points      返佣点数
        备注
        任务提交的前置检查
        If (select level from t_agent where uid = target_uid) == 3 then 提示错误:“代理商资格不符”
        成功触发模块操作：
        如果source_uid==target_uid
        更新表 t_agent where uid = source_uid :
        { reward = points }

        如果source_uid<>target_uid
        更新表 t_agent where uid = source_uid :
        {
            parentid = (select agentid from t_agent where uid = target_uid)
            reward = points
            level = (select level from t_agent where uid = target_uid) + 1
        }
        更新表 t_user where uid = source_uid:
        {
            agent_id = (select agentid from t_agent where uid = target_uid)
        }
        :return:
        """
        try:
            vti = self.vtaskitemDao.select_by_id(taskitem_id)
            source_uid = vti.source_uid
            target_uid = vti.target_uid
            _agent = self.agentDao.select_by_uid(target_uid)
            parentid = _agent.agentid
            if not _agent or _agent.level == 3:
                return '代理商资格不符'
            _level = _agent.level + 1
            if source_uid == target_uid:
                self.agentDao.update_uid(source_uid, {"reward": vti.points})
            else:
                self.agentDao.update_uid(source_uid,
                                         {"parentid": parentid, "reward": vti.points, "level": _level})
                self.userDao.update_agent(source_uid, parentid)
            return ''
        except Exception as ex:
            logging.error(ex)
        return '操作失败'

    @log_func_parameter
    def MTGroupUpdate(self, taskitem_id):
        """
        修改交易账户分组
        TRIGGER⻚      修改交易账户
        成功触发        更新MT分组模块
        失败触发        简单FAIL接⼝
        参数说明
        source_mt      MT账户
        target_mt      在这里等于上者
        mtgroup        MT分组
        备注
        成功触发操作:
        取得MT分组名
        mtname = select ntname from t_mtgroup where name = mtgroup
        移动source_mt账户到mtname组中
        :return:
        """
        try:
            vti = self.vtaskitemDao.select_by_id(taskitem_id)
            source_mt = vti.sourcemt
            _mtgroup = self.mtgroupDao.select_by_name(vti.mtgroup)
            if not _mtgroup:
                return '操作失败'
            mtname = _mtgroup.mtname
            # login, leverage, group
            isSuc = self.mtDao.doGroup(source_mt, str(_mtgroup.leverage), mtname)
            if isSuc:
                return ''
        except Exception as ex:
            logging.error(ex)
        return '操作失败'

    @log_func_parameter
    def FinDeposit(self, taskitem_id):
        """
        电汇入金
        TRIGGER⻚客户⼊⾦⻚选择电汇⼊⾦并提交
        成功触发 客户资⾦变动模块
        失败触发 简单FAIL接⼝
        参数说明
        source_uid 客户id
        target_uid 这里等于上者
        source_mt 入金MT账号
        target_mt 入金MT账号
        amount 入金金额(USD)
        exchange 入金汇率
        备注
        成功触发模块需要根据source_uid账号在t_fundflow表里新建一条credit=amount, type=11的记录
        成功触发模块需要根据source_uid账号在t_fundflow表里新建一条debit=amount, type=11的记录
        成功触发模块需要将target_mt账号里增加amount金额
        :return:
        """
        try:
            vti = self.vtaskitemDao.select_by_id(taskitem_id)
            source_uid = vti.source_uid
            source_mt = vti.sourcemt
            target_mt = vti.targetmt
            amount = vti.amount
            # login, balance, balance_type, comment="XWCRM opt"
            isSuc = self.mtDao.doBalance(str(target_mt), str(amount), "2", "XWCRM deposit")
            if isSuc:
                # uid, _type, mtlogin, transaction, extorder, comment, extpay_id, exchange, credit=0, debit=0
                self.fundflowDao.add(source_uid, 11, source_mt, '', '', '', '', vti.exchange, amount, 0)
                self.fundflowDao.add(source_uid, 11, source_mt, '', '', '', '', vti.exchange, 0, amount)
                return ''
        except Exception as ex:
            logging.error(ex)
        return '操作失败'


class TaskFail:
    def __init__(self):
        self.taskDao = TTaskDao()
        self.tasknodeDao = tasknode.TTaskNodeDao()
        self.taskitemDao = taskitem.TTaskItemDao()
        self.taskhistoryDao = taskhistory.TTaskHistoryDao()

    @log_func_parameter
    def MTWithdraw(self, taskitem_id):
        """ MT出金失败触发 """
        return ''

    @log_func_parameter
    def FinWithdraw(self, taskitem_id):
        return ''

    @log_func_parameter
    def AgentsCreate(self, taskitem_id):
        """
        新建代理商
        TRIGGER⻚新建代理商
        成功触发 更新MT代理商数据和代理商表模块
        失败触发 简单FAIL接⼝
        参数说明
        source_uid 客户id
        target_uid 代理商id，在这里等于上者
        points 返佣点数
        备注
        成功触发模块操作
        在t_agent表里添加一条记录：
        { agentid = 自动生成
         uid = source_uid
         reward = points
         level = 1
         status = ‘正常’ }
        更新t_user表 where uid = source_uid ：
        { agent_id = 上面自动生成的agentid }
        :return:
        """
        vti = self.vtaskitemDao.select_by_id(taskitem_id)
        return ''

    @log_func_parameter
    def AgentsCustomerUpdate(self, taskitem_id):
        """
        修改客户代理
        TRIGGER⻚修改客户代理
        成功触发 更新MT代理商数据和代理商表模块
        失败触发 简单FAIL接⼝
        参数说明
        source_uid 客户id
        target_uid 代理商id
        备注
        成功触发模块需要根据source_uid来更新t_user表，agent_id=target_id
        :return:
        """
        return ''

    @log_func_parameter
    def UpgradeCustomer(self, taskitem_id):
        """
        代理商升级名下客户
        TRIGGER⻚代理商升级名下客户
        成功触发 更新MT代理商数据和代理商表模块
        失败触发 简单FAIL接⼝
        参数说明
        source_uid 目标客户id
        target_uid 代理商id
        points 返佣点数
        备注
        任务提交的前置检查
        If (select level from t_agent where uid = target_uid) == 3
        then 提示错误：“代理商资格不符”
        成功触发模块需要根据source_uid在t_agent表里添加一条记录：
        { agentid = 自动生成
         uid = source_uid
         parentid = target_uid
         reward = points
         level = (select level from t_agent where uid = target_uid) + 1
         status = ‘正常’ }
        更新t_user表 where uid = source_uid ：
        { agent_id = target_uid }
        :return:
        """
        return ''

    @log_func_parameter
    def AgentsUpdate(self, taskitem_id):
        """
        修改代理商
        TRIGGER⻚修改代理商
        成功触发 更新MT代理商数据和代理商表模块
        失败触发 简单FAIL接⼝
        参数说明
        source_uid 代理商id
        target_uid 上级代理id
        points 返佣点数
        备注
        如果source_uid=target_uid，成功触发模块更新代理商表的reward=points
        如果source_uid<>target_uid，成功触发模块更新代理商表parentid=target_id
        source_uid(level)=target_uid(level)+1
        :return:
        """
        return ''

    @log_func_parameter
    def MTGroupUpdate(self, taskitem_id):
        """
        修改交易账户分组
        TRIGGER⻚修改交易账户
        成功触发 更新MT分组模块
        失败触发 简单FAIL接⼝
        参数说明
        source_mt MT账户
        target_mt 在这里等于上者
        mtgroup MT分组
        备注
        触发时，需要将新的type->name和leverage记入comment, “类型: xxx，杠杆率：xxx”
        成功触发模块需要将source_mt账户移动到mtgroup组中
        :return:
        """
        return ''

    @log_func_parameter
    def FinDeposit(self, taskitem_id):
        """
        电汇入金
        TRIGGER⻚客户⼊⾦⻚⾯选择电汇⼊⾦并提交
        成功触发 客户资⾦变动模块
        失败触发 简单FAIL接⼝
        参数说明
        source_uid 客户id
        target_uid 这里等于上者
        source_mt 入金MT账号
        target_mt 入金MT账号
        amount 入金金额(USD)
        exchange 入金汇率
        备注
        成功触发模块需要根据source_uid账号在t_fundflow表里新建一条credit=amount, type=11的记录
        成功触发模块需要根据source_uid账号在t_fundflow表里新建一条debit=amount, type=11的记录
        成功触发模块需要将target_mt账号里增加amount金额
        :return:
        """
        return ''


class TTaskDao(DBDao):
    """
    t_task表操作
    """

    @log_func_parameter
    def add(self, name, trigger, success, fail, subject, body):
        """
        添加一条任务数据
        :param name: 类型名称
        :param trigger: 发起者URL
        :param success: 成功触发
        :param fail: 失败触发
        :param subject: 标题
        :param body: 内容文本
        :return: 任务对象
        """
        _mtgroup = TTask(name, trigger, success, fail, subject, body)
        self._add(_mtgroup)
        return _mtgroup

    @log_func_parameter
    def update(self, type, name, subject, body):
        """
        已知type，更新name, subject, body
        :param type: 任务类型
        :param name: 任务名称
        :param subject: 任务主题
        :param body: 任务内容
        :return: null
        """
        self.session.query(TTask).filter(TTask.type == type).update(
            {"name": name, "subject": subject, "body": body},
            synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def select_by_trigger(self, url):
        """
        已知url，查询任务
        :param url:发起者URL
        :return: 任务对象
        """
        res = self.session.query(TTask).filter(TTask.trigger == url).order_by(TTask.createtime).first()
        return res

    @log_func_parameter
    def search_page(self, _type, subject, page=None):
        """
        #类型、主题，多条件搜索
        已知_type, subject,查询任务
        :param _type: 任务类型
        :param subject: 主题
        :param page: 分页
        :return: 任务对象
        """
        query = self.session.query(TTask)
        if _type and _type != '' and _type != 'undefined':
            query = query.filter(TTask.type == _type)
        if subject and subject != '' and subject != 'undefined':
            query = query.filter(TTask.subject == subject)
        query.order_by(TTask.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_all(self):
        """
        查询所有任务
        :return: 所有任务对象
        """
        res = self.session.query(TTask).order_by(TTask.createtime).all()
        return res

    @log_func_parameter
    def del_by_type(self, _type):
        """
        已知任务类型，删除该任务
        :param _type: 任务类型
        :return: null
        """
        res = self.session.query(TTask).filter(TTask.type == _type).order_by(TTask.createtime).first()
        self.session.delete(res)
        self.session.commit()
        self.session.close()
