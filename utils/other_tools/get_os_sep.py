#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2022/5/10 18:54
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : get_os_sep
# @describe:
"""
import os


def get_os_sep():
    """
    判断不同的操作系统的路径
    :return: windows 返回 "\", linux 返回 "/"
    """
    return os.sep
