#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: app.py
@time: 18/6/15 15:12
"""

import os

import jinja2
import tornado.web
from sqlalchemy import *
from sqlalchemy.pool import QueuePool

from handlers import handlers, ui_methods
from model import config
from utils import utils


class My404Handler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def prepare(self):
        self.set_status(404)
        self.render("404.html")


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=config.debug,
            gzip=config.gzip,
            cookie_secret=config.cookie_secret,
            login_url='/login',
        )
        super(Application, self).__init__(handlers, default_handler_class=My404Handler, **settings)

        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(settings['template_path']),
            extensions=['jinja2.ext.autoescape', 'jinja2.ext.loopcontrols', ],
            autoescape=True,
            auto_reload=config.debug)

        self.db = create_engine(config.db_conf, echo=True, poolclass=QueuePool)

        self.jinja_env.globals.update({
            'config': config,
            'format_date': utils.format_date,
            'parser_date': utils.parser_date,
        })
        self.jinja_env.filters.update(ui_methods)
