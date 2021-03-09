#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: config.py
@time: 18/6/15 15:12
"""

import os
import hashlib

# 日志级别
debug = True

# 启动参数
gzip = True
bind = '0.0.0.0'
port = int(os.getenv('PORT', 8080))
https = bool(os.getenv('ENABLE_HTTPS', False))
cookie_days = 0.002
url_prefix = ""
risk_path = 'H:\\data\\'
view_path = "http://124.67.20.228:8980/profile/view?id="

# redis缓存服务
redis_host = "10.18.97.64"
redis_port = 6379

# PostgreSQL数据库
db_params = {
    "database": "xwcrm",
    "user": "zxc",
    "password": "zxcvbnm",
    "host": "10.18.97.64",
    "port": 5432
}
DSN = "dbname=%(database)s host=%(host)s port=%(port)s user=%(user)s password=%(password)s" % db_params
db_conf = "postgresql+psycopg2://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s" % db_params
db_type = os.getenv('DB_TYPE', 'PostgreSQL')

# 密钥相关
aes_key = hashlib.sha256(os.getenv('AES_KEY', 'binux')).digest()
cookie_secret = hashlib.sha256(os.getenv('COOKIE_SECRET', 'binux')).digest()
check_task_loop = 10000
download_size_limit = 1 * 1024 * 1024
proxies = []
evil = 100

# 邮件服务
mail_domain = "smtp.honghaigy.com"
mail_port = 25
mail_from = "robomaster@honghaigy.com"
mail_password = "_r00bmaster"
mail_contentFile = "templates/welcomemail.html"

# 阿里云短信
sms_REGION = "cn-hangzhou"
sms_PRODUCT_NAME = "Dysmsapi"
sms_DOMAIN = "dysmsapi.aliyuncs.com"
sms_AccessKeyId = "LTAI9hAkoKsfr2hW"
sms_AccessKeySecret = "dsq52jlCRqM1Uv44wPb8Vhqk9m01Cx"
sms_sign_name = u'博纳斯'
sms_template_register = "SMS_138685010"
sms_template_notice = "SMS_142152736"
sms_template_modify = "SMS_138685008"

# 在线支付
lizhi_payurl = "http://lizhi.hskany.com/PayBank.aspx?"
lizhi_merchantId = "77035"
lizhi_secret = "e583411751aa4fa2f8685eeaf0bee20f"
lizhi_callbackurl = "http://124.67.20.228:8980/pay/lizhi/callback"
lizhi_hrefbackurl = "http://124.67.20.228:8980/"

try:
    from local_config import *
except ImportError:
    pass
