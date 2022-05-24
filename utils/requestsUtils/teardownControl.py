#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/5/23 14:22
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : teardownControl
# @describe: 请求后置处理

from utils.otherUtils.jsonpath import jsonpath
from utils.cacheUtils.cacheControl import Cache
from utils.requestsUtils.requestControl import RequestControl
from utils.readFilesUtils.regularControl import regular, cache_regular
from Enums.yamlData_enum import YAMLDate
from utils.otherUtils.jsonpath_date_replace import jsonpath_replace
from utils.assertUtils.assertControl import Assert


class TearDownHandler:
    """ 处理yaml格式后置请求 """

    @classmethod
    def get_teardown_data(cls, case_data):
        return case_data[YAMLDate.TEARDOWN.value]

    @classmethod
    def get_response_data(cls, case_data):
        return case_data['response_data']

    @classmethod
    def jsonpath_replace_data(cls, replace_key, replace_value):
        # 通过jsonpath判断出需要替换数据的位置
        _change_data = replace_key.split(".")
        # jsonpath 数据解析
        _new_data = jsonpath_replace(change_data=_change_data, key_name='_teardown_case')
        # 最终提取到的数据,转换成 yaml_data[xxx][xxx]
        _new_data += ' = {0}'.format(replace_value)
        return _new_data

    def teardown_handle(self, case_data):
        """ 后置处理逻辑 """
        _teardown_data = self.get_teardown_data(case_data)
        _resp_data = case_data['response_data']
        _request_data = case_data['yaml_data']['data']
        if _teardown_data is not None:
            for _data in _teardown_data:
                _case_id = _data['case_id']
                _step = _data['step']
                _teardown_case = eval(Cache('case_process').get_cache())[_case_id]
                for i in _step:
                    _replace_key = i['replace_key']
                    if i['dependent_type'] == 'response':
                        _response_dependent = jsonpath(obj=_resp_data, expr=i['jsonpath'])
                        if _response_dependent is not False:
                            _resp_case_data = _response_dependent[0]
                            exec(self.jsonpath_replace_data(replace_key=_replace_key, replace_value=_resp_case_data))
                        else:
                            raise ValueError(f"jsonpath提取失败，替换内容: {_resp_data} \n"
                                             f"jsonpath: {i['jsonpath']}")

                    elif i['dependent_type'] == 'request':
                        _request_dependent = jsonpath(obj=_request_data, expr=i['jsonpath'])
                        if _request_dependent is not False:
                            _request_case_data = _request_dependent[0]
                            exec(self.jsonpath_replace_data(replace_key=_replace_key, replace_value=_request_case_data))
                        else:
                            raise ValueError(f"jsonpath提取失败，替换内容: {_request_data} \n"
                                             f"jsonpath: {i['jsonpath']}")
                test_case = regular(str(_teardown_case))
                test_case = eval(cache_regular(test_case))
                res = RequestControl().http_request(yaml_data=test_case, dependent_switch=False)
                Assert(test_case['assert']).assert_equality(response_data=res['response_data'],
                                                            sql_data=res['sql_data'], status_code=res['status_code'])
