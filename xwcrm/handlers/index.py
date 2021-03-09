#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: index.py
@time: 18/8/01 15:12
"""

from base import *
from utils import lizhipay


class HelloWorldHandler(ApiHandler):
    def get(self):
        self.set_status(200)
        self.finish("hello world!")
        return


class LizhiCallbackHandler(ApiHandler):
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

    def get(self):
        ordernumber = self.get_argument('ordernumber', default=None)
        orderstatus = self.get_argument('orderstatus', default=None)
        paymoney = self.get_argument('paymoney', default=None)
        sysnumber = self.get_argument('sysnumber', default=None)
        attach = self.get_argument('attach', default=None)
        sign = self.get_argument('sign', default=None)

        logger.info("LizhiCallbackHandler ordernumber=%s,orderstatus=%s,paymoney=%s,sysnumber=%s,attach=%s,url=%s",
                    ordernumber, orderstatus, paymoney, sysnumber, attach, self.request.path)
        if not lizhipay.verify(ordernumber, orderstatus, paymoney, sign):
            logger.error("lizhipay.verify fail, ordernumber=%s", ordernumber)
            self.set_status(200)
            self.finish("fail")
            return
        _fundflow = self.fundflowDao.select_by_id(ordernumber)
        if not _fundflow:
            logger.error("fundflow is null, ordernumber=%s", ordernumber)
            self.set_status(400)
            self.finish(u'订单不存在')
            return
        if str(orderstatus) != "1":
            logger.error("lizhipay fail, ordernumber=%s", ordernumber)
            self.fundflowDao.update_amount(ordernumber, 19, sysnumber, attach, 0, 0)
            self.set_status(200)
            self.finish("ok")
            return
        comment = self.request.path
        paymoney = _fundflow.credit

        isBal = self.mtDao.doBalance(str(_fundflow.mtlogin), str(paymoney), "2", comment="XWCRM deposit")
        if isBal:
            self.fundflowDao.add(_fundflow.uid, 10, _fundflow.mtlogin, "", sysnumber, attach, "lizhipay",
                                 _fundflow.exchange, 0, paymoney)
            self.fundflowDao.update_amount(ordernumber, 10, sysnumber, comment, paymoney, 0)
        else:
            self.fundflowDao.add(_fundflow.uid, 99, _fundflow.mtlogin, "", sysnumber, attach, "lizhipay",
                                 _fundflow.exchange, 0, 0)
        self.set_status(200)
        self.finish("ok")
        return


handlers = [
    (r"/", HelloWorldHandler),
    (r"/pay/lizhi/callback", LizhiCallbackHandler),
]
