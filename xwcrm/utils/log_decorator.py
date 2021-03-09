#!/usr/bin/env python
# encoding: utf-8

import logging

logger = logging.getLogger("utils.log_decorator")


def log_func_parameter(func):
    def wapper(*args, **kwargs):
        param = ""
        for value in list(args[1:]):
            param = param + str(value) + ","
        if kwargs:
            param = param + str(kwargs)
        logger.info(">>> module.function=%s.%s(), parameter=%s", func.__module__, func.__name__, param)
        return func(*args, **kwargs)

    return wapper
