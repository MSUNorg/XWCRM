#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Zachary
# @license: commercial
# @contact:


from mt5_auth import *
from mt5_protocol import *
from mt5_utils import *
from mt5_connect import *
from mt5_retcode import *


# web api version
WebAPIVersion = '1881'


class MTWebAPI:
    """
    main web api class
    connection to MetaTrader5 server
    @var MTConnect
    """

    m_agent = 'XWCRM'
    m_is_crypt = False
    m_connect = None

    def __init__(self, agent='XWCRM', is_crypt=False):
        """
        Initiate a connection to MetaTrader5 server

        @param agent set a name of your agnet
        @param is_crypt not support yet

        @return MTWebAPI object
        """

        self.m_agent = agent
        self.m_is_crypt = is_crypt

    def Connect(self, ip, port, timeout, login, password):
        """
        @param ip       - ip address server
        @param port     - port server
        @param timeout  - timeout for request
        @param login    - user login
        @param password - user password

        @return MTRetCode
        """

        # create connection class
        self.m_connect = MTConnect(ip, port, timeout, self.m_is_crypt)
        # create connection
        error_code = self.m_connect.Connect()
        if error_code != MTRetCode.MT_RET_OK:
            return error_code
        # authorization to MetaTrader 5 server
        auth = MTAuthProtocol(self.m_connect, self.m_agent)
        # -crypt_rand = ''
        error_code, crypt_rand = auth.Auth(login, password, self.m_is_crypt)
        if error_code != MTRetCode.MT_RET_OK:
            # disconnect
            self.Disconnect()
            return error_code
        # if need crypt
        if(self.m_is_crypt):
            self.m_connect.SetCryptRand(crypt_rand, password)
        return MTRetCode.MT_RET_OK

    def IsConnected(self):
        """
        Check connection
        @return boll
        """

        return (self.m_connect is not None)

    def Disconnect(self):
        """
        Disconnect from MetaTrader 5 server
        @return void
        """

        if self.m_connect is not None:
            self.m_connect.Send(MTProtocolConsts.WEB_CMD_QUIT, '')
            self.m_connect.Disconnect()

    def UserAdd(self, login, password, group, leverage=100, name='', pass_investor=''):
        """
        Add a MT user with the default setup
        @param login
        @param password
        @param group
        @param name
        @param pass_investor

        @return MTRetCode
        """

        # check connection
        if self.m_connect is None:
            return MTRetCode.MT_RET_ERR_CONNECTION
        # check parameters
        if login == '' or login is None or password == '' or password is None or group == '' or group is None:
            return MTRetCode.MT_RET_ERR_PARAMS
        # setup defult name and pass_investor
        if name == '':
            name = login
        if pass_investor == '':
            pass_investor = password
        # prepare the command and data
        command = MTProtocolConsts.WEB_CMD_USER_ADD
        data = {
            MTProtocolConsts.WEB_PARAM_PASS_MAIN: password,
            MTProtocolConsts.WEB_PARAM_LOGIN: login,
            MTProtocolConsts.WEB_PARAM_PASS_INVESTOR: pass_investor,
            MTProtocolConsts.WEB_PARAM_GROUP: group,
            MTProtocolConsts.WEB_PARAM_NAME: name,
            MTProtocolConsts.WEB_PARAM_LEVERAGE: leverage
        }
        # talk to to MT server
        if self.m_connect.Send(command, data, False):
            rc = self.m_connect.Read(True, False, True)
        command, error_code = self.m_connect.ParseAnswer(rc)
        if command == MTProtocolConsts.WEB_CMD_USER_ADD:
            return MTConnect.GetRetCode(error_code[MTProtocolConsts.WEB_PARAM_RETCODE])
        else:
            return MTRetCode.MT_RET_ERROR

    def SetUserGroup(self, login, group, leverage=''):
        """
        Set a MT user's group
        @param login
        @param group

        @return MTRetCode
        :param leverage:
        """

        # check connection
        if self.m_connect is None:
            return MTRetCode.MT_RET_ERR_CONNECTION
        # check parameters
        if login == '' or login is None or group == '' or group is None:
            return MTRetCode.MT_RET_ERR_PARAMS
        # prepare the command and data
        command = MTProtocolConsts.WEB_CMD_USER_UPDATE
        data = {
            MTProtocolConsts.WEB_PARAM_LOGIN: login,
            MTProtocolConsts.WEB_PARAM_GROUP: group,
            MTProtocolConsts.WEB_PARAM_LEVERAGE: leverage
        }
        # talk to to MT server
        if self.m_connect.Send(command, data, False):
            rc = self.m_connect.Read(True, False, True)
        command, error_code = self.m_connect.ParseAnswer(rc)
        if command == MTProtocolConsts.WEB_CMD_USER_UPDATE:
            return MTConnect.GetRetCode(error_code[MTProtocolConsts.WEB_PARAM_RETCODE])
        else:
            return MTRetCode.MT_RET_ERROR

    def SetUserBalance(self, login, balance_type, balance, comment):
        """
        Set a MT user's balance
        @param login
        @param group
        @param balance_type 2 — a balance operation.
                            3 — a credit operation.
                            4 — additional adding/withdrawing.
                            5 — corrective operations.
                            6 — adding bonuses.
        @param balance the amount to change the balance. To add money, set a positive value. To withdraw money, set a negative value.

        @return MTRetCode
        """

        # check connection
        if self.m_connect is None:
            return MTRetCode.MT_RET_ERR_CONNECTION
        # check parameters
        if login == '' or login is None or balance_type == '' or balance_type is None or\
                balance == '' or balance is None:
            return MTRetCode.MT_RET_ERR_PARAMS
        # prepare the command and data
        command = MTProtocolConsts.WEB_CMD_TRADE_BALANCE
        data = {
            MTProtocolConsts.WEB_PARAM_LOGIN: login,
            MTProtocolConsts.WEB_PARAM_TYPE: balance_type,
            MTProtocolConsts.WEB_PARAM_BALANCE: balance,
            MTProtocolConsts.WEB_PARAM_COMMENT: comment,
            MTProtocolConsts.WEB_PARAM_CHECK_MARGIN: '1'
        }
        # talk to to MT server
        if self.m_connect.Send(command, data, False):
            rc = self.m_connect.Read(True, False, True)
        command, error_code = self.m_connect.ParseAnswer(rc)
        if command == MTProtocolConsts.WEB_CMD_TRADE_BALANCE:
            return MTConnect.GetRetCode(error_code[MTProtocolConsts.WEB_PARAM_RETCODE])
        else:
            return MTRetCode.MT_RET_ERROR
        pass

    def SetUserPassword(self, login, password, pass_type='MAIN'):
        """
        Set a MT user's group
        @param login
        @param passwrod
        @param pass_type defult is main passwrod, or INVESTOR, API

        @return MTRetCode
        """

        # check connection
        if self.m_connect is None:
            return MTRetCode.MT_RET_ERR_CONNECTION
        # check parameters
        if login == '' or login is None or password == '' or password is None:
            return MTRetCode.MT_RET_ERR_PARAMS
        # prepare the command and data
        command = MTProtocolConsts.WEB_CMD_USER_PASS_CHANGE
        data = {
            MTProtocolConsts.WEB_PARAM_LOGIN: login,
            MTProtocolConsts.WEB_PARAM_TYPE: pass_type,
            MTProtocolConsts.WEB_PARAM_PASSWORD: password
        }
        # talk to to MT server
        if self.m_connect.Send(command, data, False):
            rc = self.m_connect.Read(True, False, True)
        command, error_code = self.m_connect.ParseAnswer(rc)
        if command == MTProtocolConsts.WEB_CMD_USER_PASS_CHANGE:
            return MTConnect.GetRetCode(error_code[MTProtocolConsts.WEB_PARAM_RETCODE])
        else:
            return MTRetCode.MT_RET_ERROR
        pass

    def UserDepositChange(self):
        pass

    def Ping(self):
        pass
