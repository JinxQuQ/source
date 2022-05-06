#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-05-06 11:44:31
# @Author : 七月


import allure
import pytest
from common.setting import ConfigHandler
from utils.readFilesUtils.get_yaml_data_analysis import CaseData
from utils.assertUtils.assertControl import Assert
from utils.requestsUtils.requestControl import RequestControl
from utils.readFilesUtils.regularControl import regular


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
        Assert(in_data['assert']).assert_equality(response_data=res['response_data'], 
                                                  sql_data=res['sql_data'])


if __name__ == '__main__':
    pytest.main(['test_collect_addtool.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
