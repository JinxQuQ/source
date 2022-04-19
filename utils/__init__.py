#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/12/14 22:06
# @Author : 余少琪

import os
import datetime
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


def write_page_files(class_title, func_title, case_detail, case_path, yaml_path):
    """
        自动写成 py 文件
        :param yaml_path:
        :param case_path: 生成的py文件地址
        :param class_title: 类名称, 读取用例中的 caseTitle 作为类名称
        :param func_title: 函数名称 caseTitle，首字母小写
        :param case_detail: 函数描述，读取用例中的描述内容，做为函数描述
        :return:
        """
    author = GetYamlData(ConfigHandler.config_path).get_yaml_data()['TestName']
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    page = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : {now}
# @Author : {author}


from tools.requestControl import RequestControl
from tools.yamlControl import GetCaseData
from config.setting import ConfigHandler


class {class_title}(object):
    @staticmethod
    def {func_title}(inData):
        """
        {case_detail}
        :param inData:
        :return:
        """

        resp = RequestControl().HttpRequest(inData['method'], inData)
        return resp


if __name__ == '__main__':
    path = GetCaseData(ConfigHandler.data_path + r'{yaml_path}').get_yaml_case_data()[0]
    data = {class_title}().{func_title}(path)
    print(data)
        '''
    with open(case_path, 'w', encoding="utf-8") as f:
        f.write(page)


def write_testcase_file(allure_epic, allure_feature, class_title,
                        func_title, case_path, yaml_path, file_name, allure_story):
    """

        :param allure_story:
        :param file_name: 文件名称
        :param allure_epic: 项目名称
        :param allure_feature: 模块名称
        :param class_title: 类名称
        :param func_title: 函数名称
        :param case_path: case 路径
        :param yaml_path: yaml 文件路径
        :return:
        """
    author = GetYamlData(ConfigHandler.config_path).get_yaml_data()['TesterName']
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    page = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : {now}
# @Author : {author}


import allure
import pytest
from common.setting import ConfigHandler
from utils.readFilesUtils.get_yaml_data_analysis import CaseData
from utils.assertUtils.assertControl import Assert
from utils.requestsUtils.requestControl import RequestControl


TestData = CaseData(ConfigHandler.data_path + r'{yaml_path}').case_process()


@allure.epic("{allure_epic}")
@allure.feature("{allure_feature}")
class Test{class_title}:

    @allure.story("{allure_story}")
    @pytest.mark.parametrize('in_data', TestData, ids=[i['detail'] for i in TestData])
    def test_{func_title}(self, in_data, case_skip):
        """
        :param :
        :return:
        """

        res = RequestControl().http_request(in_data)
        Assert(in_data['assert']).assert_equality(response_data=res['response_data'], 
                                                  sql_data=res['sql_data'])


if __name__ == '__main__':
    pytest.main(['{file_name}', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
'''
    if not os.path.exists(case_path):
        with open(case_path, 'w', encoding="utf-8") as f:
            f.write(page)


configPath = GetYamlData(ConfigHandler.config_path).get_yaml_data()
project_name = configPath['ProjectName'][0]
tester_name = configPath['TesterName']

