#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: zxc
@contact: zhangxiongcai337@gmail.com
@site: http://lawrence-zxc.github.io/
@file: __init__.py
@time: 18/6/15 15:12
"""

import os

from model import config

handlers = []#[[(url1:handler1),(url2:handler2),...],[(urlA:handlerA),(urlB:handlerB),...]...]
ui_modules = {}
ui_methods = {}
modules = []

for file in os.listdir(os.path.dirname(__file__)):
    if not file.endswith(".py"):
        continue
    if file == "__init__.py":
        continue
    modules.append(file[:-3])

for module in modules:
    module = __import__('%s.%s' % (__package__, module), fromlist=["handlers"])
    if hasattr(module, "handlers"):
        map = []
        for element in module.handlers:
            lst = list(element)
            lst[0] = config.url_prefix + lst[0]
            element = tuple(lst)
            map.append(element)
        handlers.extend(map)
    if hasattr(module, "ui_modules"):
        ui_modules.update(module.ui_modules)
    if hasattr(module, "ui_methods"):
        ui_methods.update(module.ui_methods)
