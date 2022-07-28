#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/25 13:07
# @Author : 余少琪

import os
from utils.times_tool.time_control import now_time_day

def replace_path(path):
    """替换路径"""
    path = path.replace('$', os.sep)
    return path


def generate_path(name: str):
    # 项目路径
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root_path, name.replace('$', os.sep))


class ConfigHandler:

    # 用例路径
    case_path = generate_path("test_case$")
    # 测试用例数据路径
    data_path = generate_path('data$')

    cache_path = generate_path('Cache$')
    if not os.path.exists(cache_path):
        os.mkdir(cache_path)
    common_path = generate_path('common$')
    config_path = generate_path('common$config.yaml')

    log_path = generate_path('logs$log.log')

    info_log_path = generate_path(f'logs$info-{now_time_day()}.log')
    error_log_path = generate_path(f'logs$error-{now_time_day()}.log')
    warning_log_path = generate_path(f'logs$warning-{now_time_day()}.log')

    file_path = generate_path('Files$')

    util_path = generate_path("utils$")
    util_install_path = generate_path('utils$other_tools$install_tool$')
    # 测试报告路径
    report_path = generate_path('report')
    # 测试报告中的test_case路径
    report_html_test_case_path = generate_path("report$html$data$test-cases$")

    # 测试报告中的attachments路径
    report_html_attachments_path = generate_path("report$html$data$attachments$")

    excel_template = generate_path("utils$other_tools$allure_data$")


if __name__ == '__main__':
    print(ConfigHandler.util_install_path)
