#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/12/14 22:06
# @Author : 余少琪

import os
from common.setting import ConfigHandler
from utils.readFilesUtils.yamlControl import GetYamlData


def get_os_sep():
    """
    判断不同的操作系统的路径
    :return: windows 返回 "\", linux 返回 "/"
    """
    return os.sep


def sql_switch():
    """获取数据库开关"""
    switch = GetYamlData(ConfigHandler.config_path) \
        .get_yaml_data()['MySqlDB']["switch"]
    return switch


def get_notification_type():
    # 获取报告通知类型，是发送钉钉还是企业邮箱
    date = GetYamlData(ConfigHandler.config_path).get_yaml_data()['NotificationType']
    return date


configPath = GetYamlData(ConfigHandler.config_path).get_yaml_data()
project_name = configPath['ProjectName'][0]
tester_name = configPath['TesterName']
