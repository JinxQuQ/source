#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 17:42
# @Author : 余少琪

from enum import Enum


class RequestType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    # json 类型
    JSON = "JSON"
    # PARAMS 类型
    PARAMS = "PARAMS"
    # data 类型
    DATA = "DATA"
    # 文件类型
    FILE = 'FILE'
    # 导出文件
    EXPORT = "EXPORT"
    # 没有请求参数
    NONE = "NONE"
