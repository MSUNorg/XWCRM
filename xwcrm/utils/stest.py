#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Zachary

from mt5_api import *

# 这些内容取自系统参数表
ip = '36.102.229.227'
port = 1997
m_login = '3000'
m_password = 'Ilove125ED+'
timeout = 5

try:
    # connect to server
    mt = MTWebAPI()
    error_code = mt.Connect(ip, port, timeout, m_login, m_password)
except socket.timeout:
    print("超时")
    exit(1)
except socket.error as s_err:
    print(s_err)
    exit(1)

print(error_code)

# add user
# login = '2043'
# password = 'qwer1234'
# group = 'bonus\\pro\\50L0r0c'
# error_code = mt.UserAdd(login, password, group)
# print(error_code)
# mt.Disconnect()

# change user group
login = '5095'
group = 'bonus\\std\\50L0r0c'
leverage = '50'
error_code = mt.SetUserGroup(login, group, leverage)
print(error_code)
mt.Disconnect()

# change user balance
# login = '5095'
# balance_type = '2'
# # balance = '8966.4'
# # comment = 'XWCRM deposit'
# balance = '-9000'
# comment = 'XWCRM withdrawal'

# error_code = mt.SetUserBalance(login, balance_type, balance, comment)
# print(error_code)
# print(MTRetCode.GetError(error_code))
# mt.Disconnect()

# change user main password
# login = '5095'
# password = 'qazw4321'
# error_code = mt.SetUserPassword(login, password)
# print(error_code)
# print(MTRetCode.GetError(error_code))
# mt.Disconnect()
