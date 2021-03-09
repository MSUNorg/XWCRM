#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: mt.py
@time: 18/8/14 11:33
"""

import logging

from model import tconfig
from model.mtgroup import TMTGroupDao
from utils.mt5_api import *
from utils.log_decorator import log_func_parameter

logger = logging.getLogger('xwcrm.mt')


class MTDao:
    """
    MT操作
    """
    def __init__(self):
        self.configDao = tconfig.TConfigQuery()
        self.ip = self.configDao.get_by_name('mtserver_ip')
        self.port = int(self.configDao.get_by_name('mtserver_port'))
        self.m_login = self.configDao.get_by_name('mt_login')
        self.m_password = self.configDao.get_by_name('mt_password')
        self.timeout = int(self.configDao.get_by_name('mt_timeout'))
        _mtgroup = self.configDao.get_by_name(u'MT默认组')
        mtgroupstr = _mtgroup.replace('\\', '\\\\')
        self.mtgroup = mtgroupstr
        self.mtgroupname = _mtgroup
        self.mtapi = MTWebAPI()

    @log_func_parameter
    def doConnect(self):
        """
        建立连接
        :return:
        """
        try:
            error_code = self.mtapi.Connect(self.ip, self.port, self.timeout, self.m_login, self.m_password)
            logging.warning("doConnect once error_code %s", error_code)
            if error_code != 0:
                errmsg = MTRetCode.GetError(error_code)
                logging.error("doConnect once error_code %s,error_msg %s", error_code, errmsg)
                return False
            return True
        except Exception as ex:
            logging.error(ex)
            try:
                error_code = self.mtapi.Connect(self.ip, self.port, self.timeout, self.m_login, self.m_password)
                logging.warning("doConnect twice error_code %s", error_code)
                if error_code != 0:
                    errmsg = MTRetCode.GetError(error_code)
                    logging.error("doConnect twice error_code %s,error_msg %s", error_code, errmsg)
                    return False
                return True
            except Exception as ex:
                logging.error(ex)
                try:
                    self.mtapi.Disconnect()
                except Exception as ex:
                    logging.error(ex)
                return False

    @log_func_parameter
    def doCreate(self, login, passwd, mtgroup=None, leverage=None):
        """
           开设MT标准账户
           mtlogn=(select max(login)) from v_mtuser) + 1
           mtgroup=select mtname from t_mtgroup where type=1 and spread=0 and commission=0 and leverage=100
           statusa="出金冻结"
           role_id=select id from t_role where name="终端客户"
           mt_passwd=%8s,rand(0-9,a-z)
           group = "bonus\std\100L0r0c" 默认组名
        """
        if not self.doConnect():
            return False
        if not mtgroup:
            mtgroup = self.mtgroup
        if not leverage:
            leverage = str(TMTGroupDao().select_by_mtname(self.mtgroupname).leverage)

            logging.info("leverage: ", leverage)
        try:
            error_code = self.mtapi.UserAdd(login, passwd, mtgroup, leverage)
            logging.info("doCreate once error_code %s", error_code)
            if error_code != 0:
                errmsg = MTRetCode.GetError(error_code)
                logging.error("doCreate once error_code %s,error_msg %s", error_code, errmsg)
                return False
            return True
        except Exception as ex:
            logging.error(ex)
            return False
        finally:
            self.mtapi.Disconnect()

    @log_func_parameter
    def doGroup(self, login, leverage, mtgroup=None):
        """
        Set a MT user's group
        :param login:
        :param leverage:
        :param group:
        :return:
        """
        logging.info("[login] " + login + "[leverage] " + leverage + "[group] " + mtgroup)
        if not self.doConnect():
            return False
        if not mtgroup:
            mtgroup = self.mtgroup
        try:
            error_code = self.mtapi.SetUserGroup(login, mtgroup, leverage)
            logging.info("doGroup once error_code %s", error_code)
            if error_code != 0:
                errmsg = MTRetCode.GetError(error_code)
                logging.error("doGroup once error_code %s,error_msg %s", error_code, errmsg)
                return False
            return True
        except Exception as ex:
            logging.error(ex)
            return False
        finally:
            self.mtapi.Disconnect()

    @log_func_parameter
    def doBalance(self, login, balance, balance_type, comment="XWCRM opt"):
        """
        Set a MT user's balance
        :param login:
        :param balance:
        :param balance_type:
        :param comment:
        :return:
        """
        if not self.doConnect():
            return False
        try:
            error_code = self.mtapi.SetUserBalance(login, balance_type, balance, comment)
            logging.info("doBalance once error_code=%s,login=%s,balance_type=%s,balance=%s,comment=%s,",
                         error_code, login, balance_type, balance, comment)
            if error_code != 0:
                errmsg = MTRetCode.GetError(error_code)
                logging.error("doBalance once error_code %s,error_msg %s", error_code, errmsg)
                return False
            return True
        except Exception as ex:
            logging.error(ex)
            return False
        finally:
            self.mtapi.Disconnect()

    @log_func_parameter
    def doPasswd(self, login, password):
        """
        设定mt密码
        :param login:
        :param password:
        :return:
        """
        if not self.doConnect():
            return False
        try:
            error_code = self.mtapi.SetUserPassword(login, password)
            logging.info("doPasswd once error_code %s", error_code)
            if error_code != 0:
                errmsg = MTRetCode.GetError(error_code)
                logging.error("doPasswd once error_code %s,error_msg %s", error_code, errmsg)
                return False
            return True
        except Exception as ex:
            logging.error(ex)
            return False
        finally:
            self.mtapi.Disconnect()


if __name__ == '__main__':
    mtDao = MTDao()
    mtDao.doCreate("000", "1234567a")
