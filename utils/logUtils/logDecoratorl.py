#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 15:21
# @Author : 余少琪

from functools import wraps
from utils.logUtils.logControl import INFO, ERROR


def log_decorator(switch: bool):
    """
    封装日志装饰器, 打印请求信息
    :param switch: 定义日志开关
    :return:
    """
    def decorator(func):
        @wraps(func)
        def swapper(*args, **kwargs):
            # 判断日志为开启状态，才打印日志
            res = func(*args, **kwargs)
            # 判断日志开关为开启状态
            if switch:
                _log_msg = f"\n===========================================================================\n" \
                               f"用例标题: {res['detail']}\n" \
                               f"请求路径: {res['url']}\n" \
                               f"请求方式: {res['method']}\n" \
                               f"请求头:   {res['headers']}\n" \
                               f"请求内容: {res['request_body']}\n" \
                               f"接口响应内容: {res['response_data']}\n" \
                               f"接口响应时长: {res['res_time']} ms\n" \
                               f"Http状态码: {res['status_code']}\n" \
                               "================================================================================"
                _is_run = res['is_run']
                # 判断正常打印的日志，控制台输出绿色
                if _is_run in (True, None) and res['status_code'] == 200:
                    INFO.logger.info(_log_msg)
                else:
                    # 失败的用例，控制台打印红色
                    ERROR.logger.error(_log_msg)
            return res
        return swapper
    return decorator
