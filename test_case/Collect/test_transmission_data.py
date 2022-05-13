#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-05-12 15:32:30
# @Author : 七月


import allure
import pytest
from common.setting import ConfigHandler
from utils.readFilesUtils.get_yaml_data_analysis import CaseData
from utils.assertUtils.assertControl import Assert
from utils.requestsUtils.requestControl import RequestControl
from utils.readFilesUtils.regularControl import regular


TestData = CaseData(ConfigHandler.data_path + r'Collect/transmission_data.yaml').case_process()
re_data = regular(str(TestData))


@allure.epic("H5用户扫码使用接口")
@allure.feature("获取用户信息模块")
class TestTransmissionData:

    @allure.story("游戏机下单")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_transmission_data(self, in_data, case_skip):
        """
        :param :
        :return:
        """

        res = RequestControl().http_request(in_data)
        Assert(in_data['assert']).assert_equality(response_data=res['response_data'], 
                                                  sql_data=res['sql_data'])


if __name__ == '__main__':
    pytest.main(['test_transmission_data.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
