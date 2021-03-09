#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: sms.py
@time: 18/6/15 17:29
"""

import logging
import uuid

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from aliyunsdkcore.request import RpcRequest

import utils
from model import config
from model import tconfig

logger = logging.getLogger('hyrobot.sms')
configDao = tconfig.TConfigQuery()

# acs_client = AcsClient(config.sms_AccessKeyId, config.sms_AccessKeySecret, config.sms_REGION)
# region_provider.modify_point(config.sms_PRODUCT_NAME, config.sms_REGION, config.sms_DOMAIN)
acs_client = AcsClient(configDao.get_by_name('sms_AccessKeyId'), configDao.get_by_name('sms_AccessKeySecret'), configDao.get_by_name('sms_REGION'))
region_provider.modify_point(configDao.get_by_name('sms_PRODUCT_NAME'), configDao.get_by_name('OCR_appid'), configDao.get_by_name('sms_DOMAIN'))


class SendSmsRequest(RpcRequest):
    def __init__(self):
        RpcRequest.__init__(self, 'Dysmsapi', '2017-05-25', 'SendSms')

    def get_TemplateCode(self):
        return self.get_query_params().get('TemplateCode')

    def set_TemplateCode(self, TemplateCode):
        self.add_query_param('TemplateCode', TemplateCode)

    def get_PhoneNumbers(self):
        return self.get_query_params().get('PhoneNumbers')

    def set_PhoneNumbers(self, PhoneNumbers):
        self.add_query_param('PhoneNumbers', PhoneNumbers)

    def get_SignName(self):
        return self.get_query_params().get('SignName')

    def set_SignName(self, SignName):
        self.add_query_param('SignName', SignName)

    def get_ResourceOwnerAccount(self):
        return self.get_query_params().get('ResourceOwnerAccount')

    def set_ResourceOwnerAccount(self, ResourceOwnerAccount):
        self.add_query_param('ResourceOwnerAccount', ResourceOwnerAccount)

    def get_TemplateParam(self):
        return self.get_query_params().get('TemplateParam')

    def set_TemplateParam(self, TemplateParam):
        self.add_query_param('TemplateParam', TemplateParam)

    def get_ResourceOwnerId(self):
        return self.get_query_params().get('ResourceOwnerId')

    def set_ResourceOwnerId(self, ResourceOwnerId):
        self.add_query_param('ResourceOwnerId', ResourceOwnerId)

    def get_OwnerId(self):
        return self.get_query_params().get('OwnerId')

    def set_OwnerId(self, OwnerId):
        self.add_query_param('OwnerId', OwnerId)

    def get_SmsUpExtendCode(self):
        return self.get_query_params().get('SmsUpExtendCode')

    def set_SmsUpExtendCode(self, SmsUpExtendCode):
        self.add_query_param('SmsUpExtendCode', SmsUpExtendCode)

    def get_OutId(self):
        return self.get_query_params().get('OutId')

    def set_OutId(self, OutId):
        self.add_query_param('OutId', OutId)


def send_sms(business_id, phone_numbers, sign_name, sms_template_code, template_param=None):
    smsRequest = SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(sms_template_code)
    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)
    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)
    # 短信签名
    smsRequest.set_SignName(sign_name)
    # 数据提交方式
    # smsRequest.set_method(MT.POST)
    # 数据提交格式
    # smsRequest.set_accept_format(FT.JSON)
    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)
    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)
    return smsResponse


def send_register_code(mobile, code):
    params_ = "{\"code\":\"" + str(code) + "\"}"
    business_id = str(uuid.uuid1()).replace('-', '')
    try:
        send_sms(business_id, mobile, config.sms_sign_name, config.sms_template_register, params_)
        logger.info("send_register_code mobile=%s,sms_sign_name=%s,params=%s", mobile, config.sms_sign_name, params_)
    except Exception as ex:
        logging.error(ex)
        return


def send_notice_code(mobile, cname, mtlogin, mtpasswdd):
    params_ = "{\"cname\":\"" + str(cname) + "\", \"mtlogin\":\"" + str(mtlogin) + "\", \"mtpasswdd\":\"" + str(
        mtpasswdd) + "\"}"
    business_id = str(uuid.uuid1()).replace('-', '')
    try:
        send_sms(business_id, mobile, config.sms_sign_name, config.sms_template_notice, params_)
        logger.info("send_notice_code mobile=%s,sms_sign_name=%s,params=%s", mobile, config.sms_sign_name, params_)
    except Exception as ex:
        logging.error(ex)
        return


def send_modify_code(mobile, code):
    params_ = "{\"code\":\"" + str(code) + "\"}"
    business_id = str(uuid.uuid1()).replace('-', '')
    try:
        send_sms(business_id, mobile, config.sms_sign_name, config.sms_template_modify, params_)
        logger.info("send_modify_code mobile=%s,sms_sign_name=%s,params=%s", mobile, config.sms_sign_name, params_)
    except Exception as ex:
        logging.error(ex)
        return


if __name__ == '__main__':
    __business_id = str(uuid.uuid1()).replace('-', '')
    code = utils.create_num_vali_code()
    params = "{\"code\":\"123456\"}"
    print(send_sms(__business_id, "18912386146", u"博纳斯", params))
