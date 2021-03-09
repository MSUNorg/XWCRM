#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: ocr.py
@time: 18/11/1 21:45
"""

import logging
import urllib2
import time
import urllib
import json
import hashlib
import base64
from model import tconfig

logger = logging.getLogger('hyrobot.ocr')
configDao = tconfig.TConfigQuery()


class OCR:
    def __init__(self):
        self.APPID = configDao.get_by_name('OCR_appid')
        self.APIKey = configDao.get_by_name('OCR_apikey')
        # self.APPID = "5be91762"
        # self.APIKey = "4fc7469f122c6b5f29a02fc4fb96cf46"

    def doOCR(self, engine_type, file_content):
        base64_image = base64.b64encode(file_content)
        body = urllib.urlencode({'image': base64_image})

        # url = 'http://webapi.xfyun.cn/v1/service/v1/ocr/' + engine_type
        url = configDao.get_by_name('OCR_base') + engine_type
        param = {"engine_type": engine_type, "head_portrait": "0"}
        x_param = base64.b64encode(json.dumps(param).replace(' ', ''))
        x_time = int(int(round(time.time() * 1000)) / 1000)
        x_checksum = hashlib.md5(self.APIKey + str(x_time) + x_param).hexdigest()
        x_header = {'X-Appid': self.APPID,
                    'X-CurTime': x_time,
                    'X-Param': x_param,
                    'X-CheckSum': x_checksum}
        req = urllib2.Request(url, body, x_header)
        result = urllib2.urlopen(req)
        result = result.read()
        logger.info("xfyun ocr engine_type=%s,res=%s", engine_type, result)
        res = {}
        if result:
            json_res = json.loads(result)
            if json_res["code"] == "0":
                res = json_res["data"]
        return res

    def idcard(self, content):
        """
        {
          "code": "0",
          "data": {
            "address": "哈尔滨市南岗区人和街75号5单元601户",
            "birthday": "1986年2月23日",
            "border_covered": false,
            "complete": true,
            "error_code": 0,
            "error_msg": "ok",
            "gray_image": false,
            "head_blurred": false,
            "head_covered": false,
            "id_number": "230103198602230916",
            "name": "张志学",
            "people": "汉",
            "sex": "男",
            "type": "第二代身份证"
          },
          "desc": "success",
          "sid": "wcr00018b52@dx1daf0f4487056f1a00"
        }
        :param content:
        :return:
        """
        data = self.doOCR("idcard", content)
        if not data:
            return ""
        code = data["id_number"]
        code = code.strip()
        code = code.replace(' ', '')
        return code

    def bankcard(self, content):
        """
        {
          "code": "0",
          "data": {
            "card_number": "6222 3512 3456 5899",
            "error_code": 0,
            "error_msg": "ok",
            "holder_name": "DR.YANGKA",
            "issuer": "中国工商银行",
            "issuer_id": "01020000",
            "type": "贷记卡",
            "validate": ""
          },
          "desc": "success",
          "sid": "wcr00018b4a@dx1daf0f4486cf6f1a00"
        }
        :param content:
        :return:
        """
        data = self.doOCR("bankcard", content)
        if not data:
            return ""
        code = data["card_number"]
        code = code.strip()
        code = code.replace(' ', '')
        return code


if __name__ == '__main__':
    # f = open("H:\\msun_data\\XWCRM\\doc\\test\\yhk1.jpg", 'rb')
    f = open("H:\\msun_data\\XWCRM\\doc\\test\\sfz0.png", 'rb')
    file_content = f.read()
    ocr = OCR()
    print ocr.idcard(file_content)
