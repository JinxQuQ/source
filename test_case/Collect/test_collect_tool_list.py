#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-05-26 16:38:29
# @Author : 七月


import allure
import pytest
from common.setting import ConfigHandler
from utils.readFilesUtils.get_yaml_data_analysis import CaseData
from utils.assertUtils.assertControl import Assert
from utils.requestsUtils.requestControl import RequestControl
from utils.readFilesUtils.regularControl import regular, cache_regular
from utils.requestsUtils.teardownControl import TearDownHandler


TestData = CaseData(ConfigHandler.data_path + r'Collect/collect_tool_list.yaml').case_process()
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("收藏模块")
class TestCollectToolList:

    @allure.story("收藏网址列表接口")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_collect_tool_list(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        in_data = eval(cache_regular(str(in_data)))
        res = RequestControl().http_request(in_data)
        TearDownHandler().teardown_handle(res)
        Assert(in_data['assert']).assert_equality(response_data=res['response_data'], 
                                                  sql_data=res['sql_data'], status_code=res['status_code'])


if __name__ == '__main__':
    pytest.main(['test_collect_tool_list.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
