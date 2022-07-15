#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-06-02 15:06:23
# @Author : 七月


import allure
import pytest
from common.setting import ConfigHandler
from utils.readFilesUtils.get_yaml_data_analysis import CaseData
from utils.requestsUtils.requestControl import RequestControl
from utils.readFilesUtils.regularControl import regular

TestData = CaseData(ConfigHandler.data_path + r'Collect/collect_delete_tool.yaml').case_process()
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("收藏模块")
class TestCollectDeleteTool:

    @allure.story("删除收藏网站接口")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_collect_delete_tool(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        res = RequestControl().http_request(in_data)
        # TearDownHandler().teardown_handle(res)
        # Assert(in_data['assert']).assert_equality(response_data=res['response_data'],
        #                                           sql_data=res['sql_data'], status_code=res['status_code'])


if __name__ == '__main__':
    pytest.main(['test_collect_delete_tool.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
