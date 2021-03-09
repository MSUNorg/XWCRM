#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: lizhipay.py
@time: 18/8/14 20:33
"""

import hashlib
import logging

from model import fundflow
from model import config

logger = logging.getLogger('xwcrm.pay')

fundflowDao = fundflow.TFundflowDao()


def verify(ordernumber, orderstatus, paymoney, sign):
    """
        支付结果回调
        /?partner=77035&ordernumber=14cb3a6ea10d11e8a86eb083feb33b7e&orderstatus=1&paymoney=0.01&sysnumber=LZ770351808151358595&attach=test&sign=cf1696541348396ff4b815b6c271f4a6
        商户ID: partner(商户id,由荔枝支付API分配)
        商户订单号: ordernumber(上行过程中商户系统传入的ordernumber)
        订单结果: orderstatus(1:支付成功，非1为支付失败)
        订单金额: paymoney(单位元（人民币）)
        荔枝支付API订单号: sysnumber(此次交易中荔枝支付API接口系统内的订单ID)
        备注信息: attach(备注信息，上行中attach原样返回)
        MD5签名: sign(32位小写MD5签名值，GB2312编码)
    """
    str_param = "partner=" + config.lizhi_merchantId + "&ordernumber=" + ordernumber \
                + "&orderstatus=" + orderstatus + "&paymoney=" + paymoney + config.lizhi_secret
    m = hashlib.md5()
    m.update(str_param)
    if sign == m.hexdigest():
        return True
    return False


def dopay(uid, mtlogin, orderid, paymoney=0.01):
    # 使用系统时间戳+6位随机数字
    # orderid = int(time.time()) * 1000000 + int(check_code.create_num_vali_code())
    keys = ['partner', 'banktype', 'paymoney', 'ordernumber', 'callbackurl', 'hrefbackurl', 'attach', 'sign']
    pay_param = {
        "partner": config.lizhi_merchantId,
        "banktype": "wypay",
        "paymoney": paymoney,
        "ordernumber": orderid,
        "callbackurl": config.lizhi_callbackurl,
        "hrefbackurl": config.lizhi_hrefbackurl,
        "attach": "XWCRMdeposit",
    }
    str_param = "partner=" + pay_param["partner"] + "&banktype=" + pay_param["banktype"] \
                + "&paymoney=" + str(pay_param["paymoney"]) + "&ordernumber=" + str(pay_param["ordernumber"]) \
                + "&callbackurl=" + pay_param["callbackurl"] + config.lizhi_secret
    m = hashlib.md5()
    m.update(str_param)
    sign = m.hexdigest()

    pay_param["sign"] = sign
    url = config.lizhi_payurl
    for key in keys:
        if key == 'sign':
            url += key + "=" + str(pay_param[key])
        else:
            url += key + "=" + str(pay_param[key]) + "&"
    logger.info("lizhi_pay uid=%s,mtlogin=%s,orderid=%s,url=%s", uid, mtlogin, orderid, url)
    return url


if __name__ == '__main__':
    # print dopay(123445, "test", 11)
    print verify(config.lizhi_merchantId, "12", "1", "2.78", "aa65ac9ae0d6d74f58924749cb120e7a")
