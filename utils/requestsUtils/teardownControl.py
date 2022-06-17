#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/5/23 14:22
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : teardownControl
# @describe: 请求后置处理

from utils.otherUtils.jsonpath import jsonpath
from utils.requestsUtils.requestControl import RequestControl
from utils.readFilesUtils.regularControl import cache_regular, sql_regular, regular
from Enums.yamlData_enum import YAMLDate
from utils.otherUtils.jsonpath_date_replace import jsonpath_replace
from utils.assertUtils.assertControl import Assert
from utils.mysqlUtils.mysqlControl import MysqlDB
from utils.otherUtils.get_conf_data import sql_switch
from utils.logUtils.logControl import WARNING
from utils.cacheUtils.cacheControl import Cache


class TearDownHandler:
    """ 处理yaml格式后置请求 """

    @classmethod
    def get_teardown_data(cls, case_data):
        return case_data[YAMLDate.TEARDOWN.value]

    @classmethod
    def get_response_data(cls, case_data):
        return case_data['response_data']

    @classmethod
    def get_teardown_sql(cls, case_data):
        return case_data[YAMLDate.TEARDOWN_SQL.value]

    @classmethod
    def jsonpath_replace_data(cls, replace_key, replace_value):
        # 通过jsonpath判断出需要替换数据的位置
        _change_data = replace_key.split(".")
        # jsonpath 数据解析
        _new_data = jsonpath_replace(change_data=_change_data, key_name='_teardown_case')
        if not isinstance(replace_value, str):
            _new_data += " = '{0}'".format(replace_value)
        # 最终提取到的数据,转换成 _teardown_case[xxx][xxx]
        else:
            _new_data += " = {0}".format(replace_value)
        return _new_data

    @classmethod
    def get_cache_name(cls, replace_key, resp_case_data):
        """
        获取缓存名称，并且讲提取到的数据写入缓存
        """
        if "$set_cache{" in replace_key and "}" in replace_key:
            start_index = replace_key.index("$set_cache{")
            end_index = replace_key.index("}", start_index)
            old_value = replace_key[start_index:end_index + 2]
            cache_name = old_value[11:old_value.index("}")]
            Cache(cache_name).set_caches(resp_case_data)

    @classmethod
    def regular_testcase(cls, teardown_case):
        """处理测试用例中的动态数据"""
        test_case = regular(str(teardown_case))
        test_case = eval(cache_regular(str(test_case)))
        return test_case

    @classmethod
    def teardown_http_requests(cls, teardown_case):
        """发送后置请求"""
        test_case = cls.regular_testcase(teardown_case)
        res = RequestControl().http_request(yaml_data=test_case, dependent_switch=False)
        return res

    def teardown_handle(self, case_data):
        """ 后置处理逻辑 """
        # 拿到用例信息
        case_data = eval(cache_regular(str(case_data)))
        _teardown_data = self.get_teardown_data(case_data)
        # 获取接口的响应内容
        _resp_data = case_data['response_data']
        # 获取接口的请求参数
        _request_data = case_data['yaml_data']['data']
        # 判断如果没有 teardown
        if _teardown_data is not None:
            # 循环 teardown中的接口
            for _data in _teardown_data:
                _case_id = _data['case_id']
                _step = _data['step']
                _teardown_case = eval(Cache('case_process').get_cache())[_case_id]
                res = self.teardown_http_requests(_teardown_case)
                for i in _step:
                    # 判断请求类型为自己
                    if i['dependent_type'] == 'self_response':
                        _set_value = i['set_value']
                        # res = self.teardown_http_requests(_teardown_case)
                        _response_dependent = jsonpath(obj=res['response_data'], expr=i['jsonpath'])
                        # 如果提取到数据，则进行下一步
                        if _response_dependent is not False:
                            _resp_case_data = _response_dependent[0]
                            # 拿到 set_cache 然后将数据写入缓存
                            Cache(_set_value).set_caches(_resp_case_data)
                            self.get_cache_name(replace_key=_set_value, resp_case_data=_resp_case_data)
                        else:
                            raise ValueError(f"jsonpath提取失败，替换内容: {_resp_data} \n"
                                             f"jsonpath: {i['jsonpath']}")

                    # 判断从响应内容提取数据
                    if i['dependent_type'] == 'response':
                        _replace_key = i['replace_key']
                        _response_dependent = jsonpath(obj=_resp_data, expr=i['jsonpath'])
                        # 如果提取到数据，则进行下一步
                        if _response_dependent is not False:
                            _resp_case_data = _response_dependent[0]
                            exec(self.jsonpath_replace_data(replace_key=_replace_key, replace_value=_resp_case_data))
                        else:
                            raise ValueError(f"jsonpath提取失败，替换内容: {_resp_data} \n"
                                             f"jsonpath: {i['jsonpath']}")
                    # 判断请求中的数据
                    elif i['dependent_type'] == 'request':
                        _request_set_value = i['set_value']
                        _request_dependent = jsonpath(obj=_request_data, expr=i['jsonpath'])
                        if _request_dependent is not False:
                            _request_case_data = _request_dependent[0]
                            self.get_cache_name(replace_key=_request_set_value, resp_case_data=_request_case_data)
                        else:
                            raise ValueError(f"jsonpath提取失败，替换内容: {_request_data} \n"
                                             f"jsonpath: {i['jsonpath']}")

                    elif i['dependent_type'] == 'cache':
                        _cache_name = i['cache_data']
                        _replace_key = i['replace_key']
                        # 通过jsonpath判断出需要替换数据的位置
                        _change_data = _replace_key.split(".")
                        _new_data = jsonpath_replace(change_data=_change_data, key_name='_teardown_case')
                        # jsonpath 数据解析
                        value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
                        if any(i in _cache_name for i in value_types) is True:
                            _cache_data = Cache(_cache_name.split(':')[1]).get_cache()
                            _new_data += " = {0}".format(_cache_data)

                            # 最终提取到的数据,转换成 _teardown_case[xxx][xxx]
                        else:
                            _cache_data = Cache(_cache_name).get_cache()
                            _new_data += " = '{0}'".format(_cache_data)
                        exec(_new_data)
                print(_teardown_case)
                test_case = self.regular_testcase(_teardown_case)
                res = self.teardown_http_requests(test_case)
                Assert(test_case['assert']).assert_equality(response_data=res['response_data'],
                                                            sql_data=res['sql_data'], status_code=res['status_code'])
        self.teardown_sql(case_data)

    def teardown_sql(self, case_data):
        """处理后置sql"""
        sql_data = self.get_teardown_sql(case_data)
        _response_data = case_data['response_data']
        if sql_data is not None:
            for i in sql_data:
                if sql_switch():
                    _sql_data = sql_regular(value=i, res=_response_data)
                    print(_sql_data)
                    MysqlDB().execute(_sql_data)
                else:
                    WARNING.logger.warning(f"程序中检查到您数据库开关为关闭状态，已为您跳过删除sql: {i}")