#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: login.py
@time: 18/6/15 15:12
@description: 认证操作
"""

import base64
import decimal
import re
import uuid
from StringIO import StringIO

from base import *
from utils import ocr
from utils import send_mail
from utils import sms
from utils import utils, menu
from utils.idcard import getAge


# 管理登录提交接口
class BGLoginHandler(ApiHandler):
    def post(self):
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        password = self.get_json_argument('password', default=None)

        if not mobile and not email:
            self.error(u'请输入登录信息')
            return
        if not password:
            self.error(u'请输入密码')
            return
        _user = self.userDao.select_by_login(mobile, email)
        if not _user:
            self.error(u'不存在用户名或密码错误')
            return
        if not utils.verify(password, _user.passwd):
            self.error(u'不存在用户名或密码错误')
            return
        role_ids = _user.role_id
        pagination = self.roleDao.select_by_name("终端客户")
        for role in pagination.items:
            if role.id in role_ids:
                self.error(u'不存在用户名或密码错误')
                return

        new_token = self.update_access_token(_user.uid, _user.cname)
        me = menu.menu(role_ids)
        _access = self.roleDao.select_all_access(role_ids)
        _mtusers = self.vmtuserDao.select_by_uid(_user.uid)
        _mt = []
        for mtuser in _mtusers:
            _mt.append(
                {"mtlogin": str(mtuser.mtlogin), "mtgroup": mtuser.mtgroup, "balance": "{:.6f}".format(mtuser.balance)})
        self.success("login success",
                     {"menu": json.loads(me), "access": _access, "token": new_token, "cname": _user.cname,
                      "firstname": _user.firstname, "lastname": _user.lastname, "mobile": _user.mobile,
                      "email": _user.email, "certid": _user.certid, "bank": _user.bank, "bankbranch": _user.bankbranch,
                      "swiftcode": _user.swiftcode, "agent_id": _user.agent_id, "statusa": _user.statusa, "mt": _mt})
        return


# 登录提交接口
class LoginHandler(ApiHandler):
    def post(self):
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        password = self.get_json_argument('password', default=None)

        if not mobile and not email:
            # self.error(u'请输入登录信息')
            self.error(u'Username is required.')
            return
        if not password:
            # self.error(u'请输入密码')
            self.error(u'Password is required.')
            return
        _user = self.userDao.select_by_login(mobile, email)
        if not _user:
            # self.error(u'不存在用户名或密码错误')
            self.error(u'Invalid user name and password combination.')
            return
        if not utils.verify(password, _user.passwd):
            # self.error(u'不存在用户名或密码错误')
            self.error(u'Invalid user name and password combination.')
            return
        role_ids = _user.role_id
        pagination = self.roleDao.select_by_name("终端客户")
        for role in pagination.items:
            if role.id not in role_ids:
                # self.error(u'不存在用户名或密码错误')
                self.error(u'Invalid user name and password combination.')
                return

        if _user.statusa == '删除':
            # self.error(u'不存在用户名或密码错误')
            self.error(u'Invalid user name and password combination.')
            return
        if _user.statusa == '封禁':
            # self.err(904, u'该账户被封禁，请联系客服')
            self.err(904, u'The account is blocked, please contact customer service.')
            return
        if _user.statusa == '警告':
            self.err(907, u'允许登录，登陆后弹出警告')
            return

        new_token = self.update_access_token(_user.uid, _user.cname)
        me = menu.menu(role_ids)
        _access = self.roleDao.select_all_access(role_ids)
        logger.info("_access=%s", _access)
        _mtusers = self.vmtuserDao.select_by_uid(_user.uid)
        _mt = []
        for mtuser in _mtusers:
            _mt.append(
                {"mtlogin": str(mtuser.mtlogin), "mtgroup": mtuser.mtgroup, "balance": "{:.6f}".format(mtuser.balance)})
        self.success("login success",
                     {"menu": json.loads(me), "access": _access, "token": new_token, "cname": _user.cname,
                      "firstname": _user.firstname, "lastname": _user.lastname, "mobile": _user.mobile,
                      "email": _user.email, "certid": _user.certid, "bank": _user.bank, "bankbranch": _user.bankbranch,
                      "swiftcode": _user.swiftcode, "agent_id": _user.agent_id, "statusa": _user.statusa, "mt": _mt})
        return


# 登出清除cookies接口
class LogoutHandler(ApiHandler):
    def get(self):
        try:
            headers = self.request.headers
            token = headers['Auth-Token']
            self.del_access_token(token)
        except Exception as e:
            logger.error(e)
        self.success()
        return


# 提交注册信息验证接口
class RegisterVerifyHandler(ApiHandler):
    def post(self):
        cname = self.get_json_argument('cname', default='')
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        password = self.get_json_argument('password', default=None)
        password_confirm = self.get_json_argument('password_confirm', default=None)
        agent_id = self.get_json_argument('agent_id', default=None)
        firstname = self.get_json_argument('firstname', default='')
        lastname = self.get_json_argument('lastname', default='')

        if not cname:
            if not firstname or not lastname:
                # self.error(u'请输入用户名称')
                self.error(u'Please enter your username.')
                return
            cname = firstname + ' ' + lastname
        if not email:
            # self.error(u'请输入电子邮箱')
            self.error(u'Please enter you email address.')
            return
        """
        if not mobile:
            self.error(u'请输入手机号码')
            return
        if not re.match('1[3456789]\\d{9}', mobile):
            self.error(u'手机号错误')
            return
        """
        if email.count('@') != 1 or email.count('.') == 0:
            # self.error(u'邮箱格式不正确')
            self.error(u'Invalid email address.')
            return
        # if not re.match('\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', email):
        #    self.error(u'邮箱格式不正确')
        #    return
        if (not password) or len(password) < 8:
            # self.error(u'密码需要至少8位')
            self.error(u'Requires numbers and letters, 8-15 characters.')
            return
        if password != password_confirm:
            # self.error(u'两次密码不一致')
            self.error(u'Password entered is inconsistent.')
            return
        if mobile:
            dbuser = self.userDao.select_by_login(mobile, None)
            if dbuser:
                # self.error(u'邮箱或手机号错误')
                self.error(u'Invalid email address or mobile number.')
                return
        dbuser = self.userDao.select_by_login(None, email)
        if dbuser:
            # self.error(u'邮箱或手机号错误')
            self.error(u'Invalid email address or mobile number.')
            return
        if agent_id:
            _agent = self.agentDao.select_by_id(agent_id)
            if not _agent:
                # self.error(u'代理商编码错误')
                self.error(u'Invalid referral code.')
                return
        # self.success(u'验证通过', {"cname": cname})
        self.success(u'Verification successful.', {"cname": cname})
        return


# 提交注册信息接口
class RegisterHandler(ApiHandler):
    def post(self):
        cname = self.get_json_argument('cname', default=None)
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        password = self.get_json_argument('password', default=None)
        password_confirm = self.get_json_argument('password_confirm', default=None)
        agent_id = self.get_json_argument('agent_id', default=None)
        code = self.get_json_argument('code', default=None)
        _nc_ = self.get_json_argument('_nc_', default=None)
        firstname = self.get_json_argument('firstname', default='')
        lastname = self.get_json_argument('lastname', default='')

        if not cname:
            if not firstname or not lastname:
                # self.error(u'请输入用户名称')
                self.error(u'Please enter your username.')
                return
            cname = firstname + ' ' + lastname
        if not email:
            # self.error(u'请输入电子邮箱')
            self.error(u'Please enter you email address.')
            return
        """
        if not mobile:
            self.error(u'请输入手机号码')
            return
        if not re.match('1[3456789]\\d{9}', mobile):
            self.error(u'手机号格式不正确')
            return
        """
        if email.count('@') != 1 or email.count('.') == 0:
            # self.error(u'邮箱格式不正确')
            self.error(u'Invalid email address.')
            return
        # if not re.match('\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', email):
        # self.error(u'邮箱格式不正确')
        # return

        if (not password) or len(password) < 8:
            # self.error(u'密码需要至少8位')
            self.error(u'Requires numbers and letters, 8-15 characters.')
            return
        if password != password_confirm:
            # self.error(u'两次密码不一致')
            self.error(u'Password entered is inconsistent.')
            return
        if (not code) or len(code) < 6:
            # self.error(u'请输入验证码')
            self.error(u'Please enter verification code.')
            return
        verfi_code = self.sredis.__getitem__(_nc_)
        if not verfi_code:
            # self.error(u'验证码过期')
            self.error(u'The verification code is expired.')
            return
        if code != verfi_code:
            # self.error(u'验证码错误')
            self.error(u'The verification code is not valid.')
            return
        if mobile:
            dbuser = self.userDao.select_by_login(mobile, None)
            if dbuser:
                # self.error(u'邮箱或手机号错误')
                self.error(u'Invalid email address or mobile number.')
                return

        dbuser = self.userDao.select_by_login(None, email)
        if dbuser:
            # self.error(u'邮箱或手机号错误')
            self.error(u'Invalid email address or mobile number.')
            return

        _mtlogin = self.vmtuserDao.select_max_login() + 1
        mtlogin = str(_mtlogin)
        mtpasswd = utils.create_str_code()
        if not self.mtDao.doCreate(mtlogin, mtpasswd):
            # self.error(u'内部错误')
            self.error(u'Failed to create MT5 account, please contact customer service.')
            return

        statusa = self.configDao.get_by_name(u"注册用户状态")  # "出金冻结"
        role_name = "终端客户"
        _role = self.roleDao.select_by_name(role_name, 0)
        role_ids = [_role.id]
        mtloginids = [mtlogin]
        verfy_type = self.sredis.__getitem__(code)

        mobilev = False
        emailv = False
        if verfy_type == "mobile":
            mobilev = True
        if verfy_type == "email":
            emailv = True
        _user = self.userDao.add(cname, firstname, lastname, mobile, email, utils.encrypt(password),
                                 agent_id, statusa, role_ids, mtloginids, mobilev, emailv)
        if verfy_type == "mobile":
            sms.send_notice_code(mobile, cname, mtlogin, mtpasswd)
        if verfy_type == "email":
            send_mail.send_welcome_code(email, cname, mtlogin, mtpasswd)

        new_token = self.update_access_token(_user.uid, _user.cname, role_name)
        me = menu.menu(role_ids)
        _access = self.roleDao.select_all_access(role_ids)
        _mt = [
            {"mtlogin": str(mtlogin), "mtpasswd": mtpasswd, "balance": "{:.6f}".format(decimal.Decimal('0.0'))}
        ]
        self.success("register success",
                     {"menu": json.loads(me), "access": _access, "token": new_token, "cname": _user.cname,
                      "firstname": _user.firstname, "lastname": _user.lastname, "mobile": _user.mobile,
                      "email": _user.email, "certid": _user.certid, "bank": _user.bank, "bankbranch": _user.bankbranch,
                      "swiftcode": _user.swiftcode, "agent_id": _user.agent_id, "statusa": _user.statusa, "mt": _mt})
        return


# 注册验证码接口
class RegisterCodeHandler(ApiHandler):
    def post(self):
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        code = utils.create_num_vali_code()
        _nc_ = uuid.uuid4().hex

        if not mobile and not email:
            # self.error(u'请输入邮箱或手机号')
            self.error(u'Please enter email address or mobile number.')
            return

        if mobile:
            """
            if not re.match('1[3456789]\\d{9}', mobile):
                self.error(u'手机号错误')
                return
            """
            # 查询数据库是否已经注册
            _user = self.userDao.select_by_login(mobile, None)
            if _user:
                # self.error(u'手机号错误')
                self.error(u'The mobile number is invalid.')
                return
            sms.send_register_code(mobile, code)
            self.sredis.__setitem__(_nc_, code)
            self.sredis.__setitem__(code, "mobile")
            self.success("send RegisterCode success", {"_nc_": _nc_})
            return
        if email:
            if email.count('@') != 1 or email.count('.') == 0:
                # self.error(u'邮箱格式不正确')
                self.error(u'Invalid email address.')
                return
            _user = self.userDao.select_by_login(None, email)
            if _user:
                # self.error(u'邮箱错误')
                self.error(u'Invalid email address.')
                return
            send_mail.send_register_code(email, code)
            self.sredis.__setitem__(_nc_, code)
            self.sredis.__setitem__(code, "email")
            self.success("send RegisterCode success", {"_nc_": _nc_})
            return


# 找回密码验证码接口
class ResetpwdCodeHandler(ApiHandler):
    def post(self):
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        code = utils.create_num_vali_code()
        _ncr_ = uuid.uuid4().hex

        if not mobile and not email:
            # self.error(u'参数错误')
            self.error(u'Please enter email address or mobile number.')
            return

        if mobile:
            """
            if not re.match('1[3456789]\\d{9}', mobile):
                self.error(u'手机号错误')
                return
            """
            # 查询数据库是否已经注册
            _user = self.userDao.select_by_login(mobile, None)
            if not _user:
                # self.error(u'请输入正确的手机号码')
                self.error(u'Invalid mobile number.')
                return
            sms.send_register_code(mobile, code)
            self.sredis.__setitem__(_ncr_, code)
            self.success("send ResetpwdCode success", {"_ncr_": _ncr_})
            return
        if email:
            if email.count('@') != 1 or email.count('.') == 0:
                # self.error(u'邮箱格式不正确')
                self.error(u'Invalid email address.')
                return
            _user = self.userDao.select_by_login(None, email)
            if not _user:
                # self.error(u'邮箱错误')
                self.error(u'Invalid email address.')
                return
            send_mail.send_register_code(email, code)
            self.sredis.__setitem__(_ncr_, code)
            self.success("send ResetpwdCode success", {"_ncr_": _ncr_})
            return


# 提交找回密码接口
class ResetpwdHandler(ApiHandler):
    def post(self):
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        password = self.get_json_argument('password', default=None)
        code = self.get_json_argument('code', default=None)
        _ncr_ = self.get_json_argument('_ncr_', default=None)

        if (not code) or len(code) < 6:
            # self.error(u'请输入验证码')
            self.error(u'Please enter verification code.')
            return
        if not _ncr_:
            # self.error(u'参数错误')
            self.error(u'error')
            return
        if _ncr_ == "undefined":
            self.error(u'error')
            return
        verfi_code = self.sredis.__getitem__(_ncr_)
        if not verfi_code:
            # self.error(u'验证码过期')
            self.error(u'The verification code is expired.')
            return
        if code != verfi_code:
            # self.error(u'验证码错误')
            self.error(u'The verification code is not valid.')
            return
        if (not password) or len(password) < 8:
            # self.error(u'密码需要至少8位')
            self.error(u'Requires numbers and letters, 8-15 characters.')
            return
        if mobile:
            """
            if not re.match('1[3456789]\\d{9}', mobile):
                self.error(u'手机号错误')
                return
            """
            _user = self.userDao.select_by_login(mobile, None)
            if not _user:
                # self.error(u'请输入正确的手机号码')
                self.error(u'Invalid mobile number.')
                return
            self.userDao.update_passwd(_user.uid, utils.encrypt(password))
            self.success()
            return
        if email:
            if email.count('@') != 1 or email.count('.') == 0:
                # self.error(u'邮箱格式不正确')
                self.error(u'Invalid email address.')
                return
            _user = self.userDao.select_by_login(None, email)
            if not _user:
                # self.error(u'请输入正确的邮箱地址')
                self.error(u'Invalid email address.')
                return
            self.userDao.update_passwd(_user.uid, utils.encrypt(password))
            self.success()
            return
        # self.error(u'请至少使用邮箱或手机号')
        self.error(u'Please enter email address or mobile number.')
        return


# 我的操作
# 个人信息
class ProfileHandler(ApiHandler):
    def get(self):
        _user = self.current_user
        _mtusers = self.vmtuserDao.select_by_uid(_user.uid)
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
        _agent = self.agentDao.select_by_uid(_user.uid)
        agentid = ""
        if _agent:
            agentid = _agent.agentid
        tconfig_value = self.configDao.get_by_name(u"代理链接地址")
        url = str(tconfig_value) + agentid
        self.suc(
            {"cname": _user.cname, "firstname": _user.firstname, "lastname": _user.lastname, "mobile": _user.mobile,
             "email": _user.email, "certid": _user.certid, "bank": _user.bank, "bankbranch": _user.bankbranch,
             "bankaccount": _user.bankaccount,
             "swiftcode": _user.swiftcode, "agent_id": _user.agent_id, "statusa": _user.statusa, "mt": _mt,
             "certpic0": certpic0, "certpic1": certpic1, "bankpic0": bankpic0, "certpic0_url": _user.certpic0,
             "certpic1_url": _user.certpic1, "bankpic0_url": _user.bankpic0, "url": url, "agent": agentid,
             "country": _user.country, "state": _user.state, "address": _user.address, "addrpic0": addrpic0,
             "addrpic0_url": _user.addrpic0})
        return

    def post(self):
        _user = self.current_user
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
        statusa = self.get_json_argument('statusa', default=None)  # 前端不会传这个参数
        email = self.get_json_argument('email', default=None)
        mobile = self.get_json_argument('mobile', default=None)

        if not cname:
            if not firstname or not lastname:
                # self.error(u'请输入用户名称')
                self.error(u'Username is required.')
                return
            cname = firstname + ' ' + lastname
        if bankaccount:
            bankaccount = bankaccount.strip()
            if len(bankaccount) < 10:
                # self.error(u'请输入正确的银行卡号')
                self.error(u'Please enter correct bank account,')
                return
        if len(certid) >= 18:
            certid = certid.strip()
            if len(certid) < 15:
                # self.error(u'请输入正确的身份证号')
                self.error(u'Please enter correct ID.')
                return
            age = getAge(certid)
            if age < 18 or age > 70:
                # self.error(u'请输入正确的身份证号')
                self.error(u'Please enter correct ID.')
                return
            tconfig_value = self.configDao.get_by_name(u'证件上限')
            if tconfig_value:
                alluser = self.userDao.select_by_certid(certid)
                if len(alluser) > tconfig_value:
                    # self.error(u'该证件号已被多次使用')
                    self.error(u'The ID has been registered for many times.')
                    return
        ocr_enble = self.configDao.get_by_name(u'证件OCR')
        if ocr_enble == "yes":
            ocr_enble = True
        if ocr_enble == "no":
            ocr_enble = False
        if certpic0:
            certpic = self.picDao.select_by_id(certpic0)
            if certpic:
                idcard = certpic.ocrcode
                if ocr_enble:
                    if idcard != certid:
                        self.error(u'身份证号与证件照不符')
                        return
        if bankpic0:
            bankpic = self.picDao.select_by_id(bankpic0)
            if certpic:
                bankcode = bankpic.ocrcode
                if ocr_enble:
                    if bankcode != bankaccount:
                        self.error(u'银行卡号与银行卡照不符')
                        return
        statusa = self.configDao.get_by_name(u"认证用户状态")
        self.userDao.update_profile(_user.uid, cname, firstname, lastname, certid, bank, bankbranch, swiftcode,
                                    certpic0, certpic1, bankpic0, bankaccount, country, state, address, addrpic0,
                                    statusa, email, mobile)
        self.success("update profile success")
        return


# 在线查看图片
class ProfileViewHandler(ApiHandler):
    def get(self):
        _id = self.get_argument('id', default=None)
        if not id:
            # self.err("图片不存在")
            self.err("The picture can not be found.")
            return
        _pic = self.picDao.select_by_id(_id)
        if not _pic:
            # self.err("图片不存在")
            self.err("The picture can not be found.")
            return
        try:
            sio = StringIO(_pic.pic)
            bio = StringIO()
            base64.decode(sio, bio)
            self.set_header("Content-type", "image/png")
            self.write(bio.getvalue())
            self.flush()
            return
        except Exception as ex:
            logging.error(ex)
            self.error("view file fail")
            return


# 上传文件
class ProfileUploadHandler(ApiHandler):
    def post(self, **params):
        file_type = params["file_type"]  # idcard,bankcard,idcardback
        size = int(self.request.headers.get('Content-Length'))
        logger.info("file_type=%s,size=%s,", file_type, size)
        if size / 1000.0 > 2000:
            # self.error("上传图片不能大于2M")
            self.error("The picture size can not be larger than 2Mb.")

        _user = self.current_user
        file_metas = self.request.files['name']
        for meta in file_metas:
            try:
                sio = StringIO(meta['body'])
                bio = StringIO()
                base64.encode(sio, bio)

                _ocr = ocr.OCR()
                code = ""
                ocr_enble = self.configDao.get_by_name(u'证件OCR')
                if ocr_enble == "yes":
                    ocr_enble = True
                if ocr_enble == "no":
                    ocr_enble = False
                if file_type == "idcard" and ocr_enble:
                    code = _ocr.idcard(meta['body'])
                    if not code:
                        self.error("请上传清晰的图片")
                        return
                elif file_type == "bankcard" and ocr_enble:
                    code = _ocr.bankcard(meta['body'])
                    if not code:
                        self.error("请上传清晰的图片")
                        return
                # 入库base64字符串
                pic = self.picDao.add(_user.uid, bio.getvalue(), code)
                self.success("upload success", {"pic_url": config.view_path + pic.id, "pic_id": pic.id})
                return
            except Exception as ex:
                logging.error(ex)
                self.error("upload file fail")
                return
        self.suc()
        return


# 修改客户个人登录密码
class ProfilePasswdHandler(ApiHandler):
    def post(self):
        old_password = self.get_json_argument('old_password', default=None)
        new_password = self.get_json_argument('new_password', default=None)
        new_password_confirm = self.get_json_argument('new_password_confirm', default=None)

        if not old_password or not new_password or not new_password_confirm:
            # self.error(u'参数错误')
            self.error(u'Please enter your password.')
            return
        if (not new_password) or len(new_password) < 8:
            # self.error(u'密码需要至少8位')
            self.error(u'Requires numbers and letters, 8-15 characters.')
            return
        if new_password != new_password_confirm:
            # self.error(u'两次密码不一致')
            self.error(u'Password entered is inconsistent.')
            return
        if new_password == old_password:
            # self.error(u'前后2次密码一样')
            self.error(u"Can't be the same as current password.")
            return
        _user = self.current_user
        if not utils.verify(old_password, _user.passwd):
            # self.error(u'不存在用户名或密码错误')
            self.error(u'Invalid user name and password combination.')
            return

        self.userDao.update_passwd(_user.uid, utils.encrypt(new_password))
        self.success()
        return


# 个人客户手机号邮箱修改验证码
class ProfileLoginidCodeHandler(ApiHandler):
    def post(self):
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        code = utils.create_num_vali_code()
        _plc_ = uuid.uuid4().hex

        if mobile:
            """
            if not re.match('1[3456789]\\d{9}', mobile):
                self.error(u'手机号错误')
                return
            """
            bak_user = self.userDao.select_by_login(mobile)
            if bak_user:
                # self.error(u'手机号码已经存在')
                self.error(u'The mobile number has already been registered.')
                return

            sms.send_modify_code(mobile, code)
            self.sredis.__setitem__(_plc_, code)
            logger.error("code=%s,_plc_=%s", code, _plc_)
            self.success("send Profile Loginid Code success", {"_plc_": _plc_})
            return
        if email:
            if email.count('@') != 1 or email.count('.') == 0:
                # self.error(u'邮箱格式不正确')
                self.error(u'Invalid email address.')
                return
            bak_user = self.userDao.select_by_login(None, email)
            if bak_user:
                # self.error(u'邮箱已经存在')
                self.error(u'The email address has already been registered.')
                return

            send_mail.send_register_code(email, code)
            self.sredis.__setitem__(_plc_, code)
            logger.error("code=%s,_plc_=%s", code, _plc_)
            self.success("send Profile Loginid Code success", {"_plc_": _plc_})
            return


# 个人客户手机号邮箱修改
class ProfileLoginidHandler(ApiHandler):
    def post(self):
        mobile = self.get_json_argument('mobile', default=None)
        email = self.get_json_argument('email', default=None)
        code = self.get_json_argument('code', default=None)
        _plc_ = self.get_json_argument('_plc_', default=None)

        if (not code) or len(code) < 6:
            # self.error(u'请输入验证码')
            self.error(u'Please enter verification code.')
            return
        verfi_code = self.sredis.__getitem__(_plc_)
        logger.error("code=%s,verfi_code=%s", code, verfi_code)
        if not verfi_code:
            # self.error(u'验证码过期')
            self.error(u'The verification code is expired.')
            return
        if code != verfi_code:
            # self.error(u'验证码错误')
            self.error(u'The verification code is not valid.')
            return
        _user = self.current_user
        _mobile = mobile
        _email = email
        if email and mobile:
            """
            if not re.match('1[3456789]\\d{9}', mobile):
                self.error(u'手机号错误')
                return
            """
            if email.count('@') != 1 or email.count('.') == 0:
                # self.error(u'邮箱格式不正确')
                self.error(u'Invalid email address.')
                return
            bak_user = self.userDao.select_by_login(mobile)
            if bak_user:
                # self.error(u'手机号码已经存在')
                self.error(u'The mobile number has already been registered.')
                return
            bak_user = self.userDao.select_by_login(None, email)
            if bak_user:
                # self.error(u'邮箱已经存在')
                self.error(u'The email address has already been registered.')
                return
            self.userDao.update_m_e(_user.uid, _mobile, _email)
            self.success()
            return
        if mobile:
            """
            if not re.match('1[3456789]\\d{9}', mobile):
                self.error(u'手机号错误')
                return
            """
            bak_user = self.userDao.select_by_login(mobile)
            if bak_user:
                # self.error(u'手机号码已经存在')
                self.error(u'The mobile number has already been registered.')
                return
            if _user.mobile:
                _email = _user.email
        if email:
            if email.count('@') != 1 or email.count('.') == 0:
                # self.error(u'邮箱格式不正确')
                self.error(u'Invalid email address.')
                return
            bak_user = self.userDao.select_by_login(None, email)
            if bak_user:
                # self.error(u'邮箱已经存在')
                self.error(u'The email address has already been registered.')
                return
            if _user.mobile:
                _mobile = _user.mobile
        self.userDao.update_m_e(_user.uid, _mobile, _email)
        self.success()
        return


handlers = [
    (r"/bg/login", BGLoginHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/register/verify", RegisterVerifyHandler),
    (r"/register", RegisterHandler),
    (r"/register/code", RegisterCodeHandler),
    (r"/resetpwd/code", ResetpwdCodeHandler),
    (r"/resetpwd", ResetpwdHandler),

    (r"/profile/loginid/code", ProfileLoginidCodeHandler),
    (r"/profile/loginid", ProfileLoginidHandler),
    (r"/profile/info", ProfileHandler),
    (r"/profile/view", ProfileViewHandler),
    (r"/profile/upload/?(?P<file_type>[A-Za-z0-9-]+)?", ProfileUploadHandler),
    (r"/profile/passwd", ProfilePasswdHandler),
]
