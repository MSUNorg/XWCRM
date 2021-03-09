#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: send_mail.py
@time: 18/6/15 18:54
"""

import logging
import smtplib
from email.mime.text import MIMEText

from model import tconfig

from log_decorator import log_func_parameter

logger = logging.getLogger('xwcrm.mail')

configDao = tconfig.TConfigQuery()

@log_func_parameter
def build_handle(mail_from,mail_to, send_msg,local_hostname=None,timeout=5,login=True):
    try:

        # handle = smtplib.SMTP(config.mail_domain, config.mail_port)
        mail_domain = configDao.get_by_name('mail_domain')
        mail_password = configDao.get_by_name('mail_password')
        mail_type = configDao.get_by_name('mail_type')
        handle = None
        if mail_type == 'TLS':
            handle = smtplib.SMTP(mail_domain, local_hostname, timeout)
            handle.starttls()
        if mail_type == 'SSL':
            handle = smtplib.SMTP_SSL(mail_domain, local_hostname, timeout)
        if mail_type == 'PLAN':
            handle = smtplib.SMTP(mail_domain, local_hostname, timeout)
        if mail_type == 'LMTP':
            handle = smtplib.LMTP(mail_domain, local_hostname)
        if login :
            handle.login(mail_from, mail_password)

        handle.sendmail(mail_from, mail_to, send_msg)
        handle.close()
    except Exception as e:
        logger.error(e)


@log_func_parameter
def send_text(mail_to, subject, content):
    try:
        mail_from = configDao.get_by_name('mail_from')
        send_msg = MIMEText(content, 'html', 'utf-8')
        send_msg['Subject'] = subject
        send_msg['From'] = mail_from
        send_msg['To'] = mail_to
        build_handle(mail_from, mail_to, send_msg.as_string())
    except Exception as e:
        logger.error(e)
        pass

@log_func_parameter
def send_text_cc(mail_to, mail_cc, subject, content):
    try:
        handle = build_handle()
        mail_from = configDao.get_by_name('mail_from')
        send_msg = MIMEText(content, 'html', 'utf-8')
        send_msg['Subject'] = subject
        send_msg['From'] = mail_from
        send_msg['To'] = ', '.join(mail_to)
        send_msg['Cc'] = ', '.join(mail_cc)
        handle.sendmail(mail_from, mail_to + mail_cc, send_msg.as_string())
        handle.close()
    except Exception as e:
        logger.error(e)
        pass

@log_func_parameter
def send_mime(mail_to, subject, content):
    try:
        handle = build_handle()
        mail_from = configDao.get_by_name('mail_from')
        send_msg = MIMEText(content, 'html', 'utf-8')
        send_msg['Subject'] = subject
        send_msg['From'] = mail_from
        send_msg['To'] = mail_to
        handle.sendmail(mail_from, mail_to, send_msg.as_string())
        handle.close()
    except Exception as e:
        logger.error(e)
        pass

@log_func_parameter
def send_register_code(email, code):
    subject = u'[BonusFinance] Verification code!'
    msg1 = u'Your verification code is %s\n' % code
    #msg2 = u'您的验证码是%s' % code
    msg = msg1 # + msg2
    send_text(email, subject, msg)
    logger.info("send_register_code email=%s,subject=%s,msg=%s", email, subject, msg)

@log_func_parameter
def send_notice_code(email, cname, mtlogin, mtpasswdd):
    subject = u'新用户欢迎邮件'
    msg = u'欢迎%s注册为博纳斯用户！您的MT账号已经开通，账号为%s，密码为%s' % (cname, mtlogin, mtpasswdd)
    send_text(email, subject, msg)
    logger.info("send_notice_code email=%s,subject=%s,msg=%s", email, subject, msg)

@log_func_parameter
def send_welcome_code(email, cname, mtlogin, mtpasswdd):
    subject = u'[BonusFinance] New user registered successfully!'
    # msg = u'欢迎%s注册为博纳斯用户！您的MT账号已经开通，账号为%s，密码为%s' % (cname, mtlogin, mtpasswdd)

    # welcomemail = open('templates/welcomemail2.html', 'r+')
    welcomemail = open(configDao.get_by_name('mail_contentFile'), 'r+')
    content = welcomemail.read()
    if '{{cname}}' in content:
        content = content.replace('{{cname}}', cname)
    if '{{mtlogin}}' in content:
        content = content.replace('{{mtlogin}}', mtlogin)
    if '{{mtpasswdd}}' in content:
        content = content.replace('{{mtpasswdd}}', mtpasswdd)
    welcomemail.flush()
    welcomemail.close()

    send_text(email, subject, content)
    logger.info("send_welcome_code email=%s,subject=%s", email, subject)

@log_func_parameter
def send_modify_code(email, code):
    subject = u'修改手机号的验证码'
    msg = u'验证码%s，您正在尝试变更重要信息，请妥善保管账户信息' % code
    send_text(email, subject, msg)
    logger.info("send_modify_code email=%s,subject=%s,msg=%s", email, subject, msg)


if __name__ == '__main__':
    send_register_code('zhangxiongcai337@163.com', "123456")
    # send_notice_code('zhangxiongcai337@163.com', "zxc337", "mtlogin", "mtpasswdd")
