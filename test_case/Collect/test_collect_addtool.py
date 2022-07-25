#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-07-25 16:39:10
# @Author : 七月


import allure
import pytest
from common.setting import ConfigHandler
from utils.read_files_tools.get_yaml_data_analysis import CaseData
from utils.assertion.assert_control import Assert
from utils.requestsUtils.requestControl import RequestControl
from utils.read_files_tools.regular_control import regular
from utils.requestsUtils.teardownControl import TearDownHandler


TestData = CaseData(ConfigHandler.data_path + r'Collect/collect_addtool.yaml').case_process()
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("收藏模块")
class TestCollectAddtool:

    @allure.story("收藏网址接口")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_collect_addtool(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        res = RequestControl().http_request(in_data)
        TearDownHandler().teardown_handle(res)
        Assert(in_data['assert']).assert_equality(response_data=res['response_data'], 
                                                  sql_data=res['sql_data'], status_code=res['status_code'])


if __name__ == '__main__':
    pytest.main(['test_collect_addtool.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
