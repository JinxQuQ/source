#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-08-11 10:26:59


import allure
import pytest
from common.setting import ConfigHandler
from utils.read_files_tools.get_yaml_data_analysis import CaseData
from utils.assertion.assert_control import Assert
from utils.requests_tool.request_control import RequestControl
from utils.read_files_tools.regular_control import regular
from utils.requests_tool.teardown_control import TearDownHandler


TestData = CaseData(ConfigHandler.data_path + r'UserInfo/get_user_info.yaml').case_process()
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("个人信息模块")
class TestGetUserInfo:

    @allure.story("个人信息接口")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_get_user_info(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        res = RequestControl(in_data).http_request()
        TearDownHandler(res).teardown_handle()
        Assert(in_data['assert_data']).assert_equality(response_data=res.response_data,
                                                       sql_data=res.sql_data, status_code=res.status_code)


if __name__ == '__main__':
    pytest.main(['test_get_user_info.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
