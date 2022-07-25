#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2022/5/10 18:55
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : get_conf_data
# @describe:
"""

from common.setting import ConfigHandler
from utils.read_files_tools.yaml_control import GetYamlData
conf = GetYamlData(ConfigHandler.config_path).get_yaml_data()


def sql_switch():
    """获取数据库开关"""
    switch = conf['MySqlDB']["switch"]
    return switch


def get_notification_type():
    """获取报告通知类型，是发送钉钉还是企业邮箱"""
    date = conf['NotificationType']
    return date


def get_excel_report_switch():
    """获取excel报告开关"""
    excel_report_switch = conf['excel_report']
    return excel_report_switch


def get_mirror_url():
    """获取镜像源"""
    mirror_url = conf['mirror_source']
    return mirror_url


project_name = conf['ProjectName'][0]
tester_name = conf['TesterName']
