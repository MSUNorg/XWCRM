#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: user.py
@time: 18/6/20 17:33
"""

from models import DBDao, TUser, TPic, TAgent, Pagination, TConfig
from sqlalchemy import or_
from utils.log_decorator import log_func_parameter

class UserDao(DBDao):
    '''
    t_user表操作
    '''

    @log_func_parameter
    def add(self, cname, firstname, lastname, mobile, email, passwd, agent_id, statusa,
            role_id, mtloginids=None, mobilev=False, emailv=False):
        '''
        添加一条用户数据
        :param cname: 用户名
        :param mobile: 手机号
        :param email: 邮箱
        :param passwd: 密码
        :param agent_id: 代理
        :param statusa: 状态a
        :param role_id: 用户角色
        :param mtloginids: MT账户
        :return: 用户对象
        '''
        user = TUser(cname, firstname, lastname, mobile, email, passwd, agent_id, statusa, role_id,
                     mtloginids, mobilev, emailv)
        self._add(user)
        return user

    @log_func_parameter
    def update_mtloginids(self, uid, mtloginids):
        '''
        已知用户id，更新MT账户
        :param uid: 用户id
        :param mtloginids: 新MT账户
        :return: null
        '''
        self.session.query(TUser).filter(TUser.uid == uid).update({"mtlogin": mtloginids}, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update_passwd(self, uid, newpass):
        '''
         已知用户id，更新密码
        :param uid: 用户id
        :param newpass: 新密码
        :return: null
        '''
        self.session.query(TUser).filter(TUser.uid == uid).update({"passwd": newpass}, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update_m_e(self, uid, mobile, email):
        '''
        已知用户id，更新手机号、邮箱
        :param uid: 用户id
        :param mobile: 手机号
        :param email: 邮箱
        :return: null
        '''
        self.session.query(TUser).filter(TUser.uid == uid).update({"mobile": mobile, "email": email},
                                                                  synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update_info_passwd(self, uid, cname, email, passwd, role_id):
        '''
        已知用户id，更新cname, email, passwd, role_id
        :param uid: 用户id
        :param cname: 用户名
        :param email: 邮箱
        :param passwd: 密码
        :param role_id: 角色
        :return: null
        '''
        self.session.query(TUser).filter(TUser.uid == uid).update({"cname": cname, "email": email, "passwd": passwd,
                                                                   "role_id": role_id}, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update_info(self, uid, cname, email, role_id):
        '''
        已知用户id，更新cname, email, role_id
        :param uid: 用户id
        :param cname: 用户名
        :param email: 邮箱
        :param role_id: 角色
        :return: null
        '''
        self.session.query(TUser).filter(TUser.uid == uid).update({"cname": cname, "email": email,
                                                                   "role_id": role_id}, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update_agent(self, uid, agent_id):
        '''
        已知用户id，更新agent_id
        :param uid: 用户id
        :param agent_id: 新代理
        :return: null
        '''
        self.session.query(TUser).filter(TUser.uid == uid).update({"agent_id": agent_id}, synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update_agent_role(self, uid, agent_id, role_id):
        '''
        已知用户id，更新agent_id, role_id
        :param uid: 用户id
        :param agent_id: 代理
        :param role_id: 角色
        :return: null
        '''
        self.session.query(TUser).filter(TUser.uid == uid).update({"agent_id": agent_id, "role_id": role_id},
                                                                  synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def update_profile(self, uid, cname, firstname, lastname, certid, bank, bankbranch, swiftcode, certpic0, certpic1,
                       bankpic0, bankaccount, country, state, address, addrpic0, statusa, email, mobile):
        '''
        已知用户id，更新cname, firstname, lastname, certid, bank, bankbranch, swiftcode, certpic0, certpic1,bankpic0, bankaccount
        :param uid: 用户id
        :param cname: 中文名
        :param firstname: 英文名
        :param lastname: 英文性
        :param certid: 证件号
        :param bank: 开户行
        :param bankbranch: 支行名称
        :param swiftcode:电汇号
        :param certpic0:证件图片0
        :param certpic1:证件图片1
        :param bankpic0:银行卡图片0
        :param bankaccount:银行账户
        :return:null
        '''
        if statusa:
            # statusa存在，说明是内部用户调用的该方法
            if bankaccount:
                self.session.query(TUser).filter(TUser.uid == uid).update(
                    {"cname": cname, "firstname": firstname, "lastname": lastname,
                     "certid": certid, "bank": bank, "bankbranch": bankbranch, "swiftcode": swiftcode,
                     "certpic0": certpic0, "certpic1": certpic1, "bankpic0": bankpic0, "bankaccount": bankaccount,
                     "country": country, "state": state, "address": address, "addrpic0": addrpic0, "statusa": statusa,
                     "mobile": mobile, "email": email},
                    synchronize_session=False)
            else:
                self.session.query(TUser).filter(TUser.uid == uid).update(
                    {"cname": cname, "firstname": firstname, "lastname": lastname,
                     "certid": certid, "bank": bank, "bankbranch": bankbranch,
                     "swiftcode": swiftcode, "certpic0": certpic0, "certpic1": certpic1, "bankpic0": bankpic0,
                     "country": country, "state": state, "address": address, "addrpic0": addrpic0, "statusa": statusa,
                     "mobile": mobile, "email": email},
                    synchronize_session=False)
        else:
            # statusa不存在，说明是外部客户调用的该方法
            statusa = self.session.query(TConfig.value).filter(TConfig.name == u"认证用户状态").first()  # 完善信息，状态变"正常"
            if bankaccount:
                self.session.query(TUser).filter(TUser.uid == uid).update(
                    {"cname": cname, "firstname": firstname, "lastname": lastname,
                     "certid": certid, "bank": bank, "bankbranch": bankbranch, "swiftcode": swiftcode,
                     "certpic0": certpic0, "certpic1": certpic1, "bankpic0": bankpic0, "bankaccount": bankaccount,
                     "country": country, "state": state, "address": address, "addrpic0": addrpic0, "statusa": statusa},
                    synchronize_session=False)
            else:
                self.session.query(TUser).filter(TUser.uid == uid).update(
                    {"cname": cname, "firstname": firstname, "lastname": lastname,
                     "certid": certid, "bank": bank, "bankbranch": bankbranch,
                     "swiftcode": swiftcode, "certpic0": certpic0, "certpic1": certpic1, "bankpic0": bankpic0,
                     "country": country, "state": state, "address": address, "addrpic0": addrpic0, "statusa": statusa},
                    synchronize_session=False)
        self.session.commit()
        self.session.close()

    @log_func_parameter
    def select_by_uid(self, uid):
        '''
        已知用户id，查询用户
        :param uid:
        :return: 用户对象
        '''
        res = self.session.query(TUser).filter(TUser.uid == uid).order_by(TUser.createtime).first()
        return res

    @log_func_parameter
    def select_by_certid(self, certid):
        '''
        已知certid，查询用户
        :param certid: 证件号
        :return: 用户
        '''
        res = self.session.query(TUser).filter(TUser.certid == certid).order_by(TUser.createtime).all()
        return res

    @log_func_parameter
    def select_by_login(self, mobile=None, email=None):
        '''
        已知mobile, email，查询用户
        :param mobile: 手机号
        :param email: 邮箱
        :return: 用户对象
        '''
        query = self.session.query(TUser)
        if mobile and mobile != '' and mobile != 'undefined':
            query = query.filter(TUser.mobile == mobile)
        if email and email != '' and email != 'undefined':
            query = query.filter(TUser.email == email)
        res = query.order_by(TUser.createtime).first()
        return res

    # isinner=False查询外部用户, isinner=True查询内部用户
    @log_func_parameter
    def select_by_params_page(self, cname, role_id, isinner=False, page=None):
        '''
        已知cname, role_id, isinner=False，查询用户
        :param cname: 用户名
        :param role_id: 角色
        :param isinner: boolean
        :param page: 分页
        :return: 用户对象
        '''
        query = self.session.query(TUser)
        if cname and cname != '' and cname != 'undefined':
            query = query.filter(TUser.cname == cname)
        if role_id and role_id != '' and role_id != 'undefined':
            query = query.filter(TUser.role_id == role_id)
        if not isinner:
            query = query.filter(TUser.mtlogin.isnot(None))
        else:
            query = query.filter(or_(TUser.mtlogin.is_(None), TUser.mtlogin == '{}'))
        query.order_by(TUser.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    # 外部客户查询接口
    @log_func_parameter
    def search_page(self, cname, mobile, email, certid, mtlogin, agent_id, bankaccount, page=None):
        '''
        已知cname, mobile, email, certid, mtlogin, agent_id, bankaccount,查询用户
        :param cname: 用户名
        :param mobile: 手机号
        :param email: 邮箱
        :param certid: 证件号
        :param mtlogin: MT账户
        :param agent_id: 代理
        :param bankaccount: 银行账户
        :param page: 分页
        :return: 用户对象
        '''
        query = self.session.query(TUser)
        query = query.filter(TUser.mtlogin.isnot(None))
        if cname and cname != '' and cname != 'undefined':
            query = query.filter(TUser.cname == cname)
        if mobile and mobile != '' and mobile != 'undefined':
            query = query.filter(TUser.mobile == mobile)
        if email and email != '' and email != 'undefined':
            query = query.filter(TUser.email == email)
        if certid and certid != '' and certid != 'undefined':
            query = query.filter(TUser.certid == certid)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(TUser.numbers.contains([mtlogin]))
        if agent_id and agent_id != '' and agent_id != 'undefined':
            query = query.filter(TUser.agent_id == agent_id)
        if bankaccount and bankaccount != '' and bankaccount != 'undefined':
            query = query.filter(TUser.bankaccount == bankaccount)
        query.order_by(TUser.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    # 外部客户查询接口
    @log_func_parameter
    def search_page_join(self, cname, mobile, email, certid, mtlogin, agent_id, bankaccount, page=None):
        '''
        已知cname, mobile, email, certid, mtlogin, agent_id, bankaccount，查询用户、及其代理信息
        :param cname: 中文名称
        :param mobile: 手机号
        :param email: 邮箱
        :param certid: 证件号
        :param mtlogin: MT账户
        :param agent_id: 代理
        :param bankaccount: 银行账户
        :param page: 分页
        :return: 用户、及其代理信息
        '''
        query = self.session.query(TUser.uid, TUser.cname, TUser.mobile, TUser.email, TUser.certid, TUser.bankaccount,
                                   TUser.mtlogin, TUser.agent_id, TAgent.agentid, TAgent.level, TAgent.status,
                                   TAgent.createtime)
        query = query.join(TAgent, TUser.uid == TAgent.uid)
        if cname and cname != '' and cname != 'undefined':
            query = query.filter(TUser.cname == cname)
        if mobile and mobile != '' and mobile != 'undefined':
            query = query.filter(TUser.mobile == mobile)
        if email and email != '' and email != 'undefined':
            query = query.filter(TUser.email == email)
        if certid and certid != '' and certid != 'undefined':
            query = query.filter(TUser.certid == certid)
        if mtlogin and mtlogin != '' and mtlogin != 'undefined':
            query = query.filter(TUser.mtlogin.contains([mtlogin]))
        if agent_id and agent_id != '' and agent_id != 'undefined':
            query = query.filter(TUser.agent_id == agent_id)
        if bankaccount and bankaccount != '' and bankaccount != 'undefined':
            query = query.filter(TUser.bankaccount == bankaccount)
        query.order_by(TUser.createtime)
        if page == -1:
            return query.all()
        if not page or page == '' or page == 'undefined':
            page = 1
        return Pagination(query=query, page=page)

    @log_func_parameter
    def select_all(self):
        '''
        查询所有用户
        :return: 用户对象
        '''
        res = self.session.query(TUser).order_by(TUser.createtime).all()
        return res

    @log_func_parameter
    def del_by_uid(self, uid):
        '''
        已知用户id，删除该用户
        :param uid:
        :return: null
        '''
        res = self.session.query(TUser).filter(TUser.uid == uid).order_by(TUser.createtime).first()
        self.session.delete(res)
        self.session.commit()
        self.session.close()


class PicDao(DBDao):
    """
    t_pic表操作
    """

    @log_func_parameter
    def add(self, uid, _pic, ocrcode):
        """
        添加一条数据
        :param uid: 用户id
        :param _pic: 图片流
        :param ocrcode: OCR识别码
        :return: 图片对象
        """
        obj = TPic(uid, _pic, ocrcode)
        self._add(obj)
        return obj

    @log_func_parameter
    def select_by_id(self, _id):
        """
        已知图片id，查询图片
        :param _id: 图片id
        :return: 图片对象
        """
        res = self.session.query(TPic).filter(TPic.id == _id).first()
        return res

    @log_func_parameter
    def select_by_uid(self, uid):
        """
        已知用户id，查询所有图片
        :param uid: 用户id
        :return: 图片对象
        """
        res = self.session.query(TPic).filter(TPic.uid == uid).all()
        return res
