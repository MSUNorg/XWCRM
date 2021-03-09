#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: run.py
@time: 18/6/15 15:12
"""

import logging.config
import os
import sys

import tornado.log
import yaml
from tornado.httpserver import HTTPServer

from app import Application
from model import config

reload(sys)
sys.setdefaultencoding('utf-8')


def write_Pid_File():
    pid = str(os.getpid())
    f = open('/tmp/' + 'xwcrm.pid', 'w')
    f.write(pid)
    f.close()


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.config.dictConfig(yaml.load(open('logging.yaml', 'r')))
    if len(sys.argv) > 2 and sys.argv[1] == '-p' and sys.argv[2].isdigit():
        port = int(sys.argv[2])
    else:
        port = config.port
    # write_Pid_File()

    http_server = HTTPServer(Application(), xheaders=True)
    http_server.bind(port, config.bind)
    http_server.start()
    io_loop = tornado.ioloop.IOLoop.instance()
    logging.info("http server started on %s:%s", config.bind, port)
    io_loop.start()
