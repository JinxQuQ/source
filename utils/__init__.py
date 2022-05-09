#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/12/14 22:06
# @Author : 余少琪

import os
from common.setting import ConfigHandler
from utils.readFilesUtils.yamlControl import GetYamlData

conf = GetYamlData(ConfigHandler.config_path).get_yaml_data()


def get_os_sep():
    """
    判断不同的操作系统的路径
    :return: windows 返回 "\", linux 返回 "/"
    """
    return os.sep


def sql_switch():
    """获取数据库开关"""
    switch = conf['MySqlDB']["switch"]
    return switch


def get_notification_type():
    # 获取报告通知类型，是发送钉钉还是企业邮箱
    date = conf['NotificationType']
    return date


def get_excel_report_switch():
    """获取excel报告开关"""
    excel_report_switch = conf['excel_report']
    return excel_report_switch


project_name = conf['ProjectName'][0]
tester_name = conf['TesterName']
