#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 12:52
# @Author : 余少琪
import os
import random
import time
import urllib

import jsonpath
import requests
from typing import Any
import urllib3
from utils.otherUtils.get_conf_data import sql_switch
from requests_toolbelt import MultipartEncoder
from utils.logUtils.logDecoratorl import log_decorator
from utils.mysqlUtils.mysqlControl import MysqlDB
from Enums.requestType_enum import RequestType
from Enums.yamlData_enum import YAMLDate
from common.setting import ConfigHandler
from utils.logUtils.runTimeDecoratorl import execution_duration
from utils.otherUtils.allureDate.allure_tools import allure_step, allure_step_no, allure_attach
from utils.readFilesUtils.regularControl import cache_regular
from utils.requestsUtils.set_current_request_cache import SetCurrentRequestCache
from utils.cacheUtils.cacheControl import Cache
from utils.logUtils.logControl import ERROR
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestControl:
    """ 封装请求 """

    @classmethod
    def _check_params(cls, response, yaml_data, headers, cookie, res_time, status_code, teardown, teardown_sql) -> Any:
        """ 抽离出通用模块，判断 http_request 方法中的一些数据校验 """
        # 判断数据库开关，开启状态，则返回对应的数据
        if sql_switch() and yaml_data['sql'] is not None:
            sql_data = MysqlDB().assert_execution(sql=yaml_data['sql'], resp=response)
            return {"response_data": response, "sql_data": sql_data, "yaml_data": yaml_data,
                    "headers": headers, "cookie": cookie, "res_time": res_time, "status_code": status_code,
                    "teardown": teardown, "teardown_sql": teardown_sql}
        else:
            # 数据库关闭走的逻辑
            res = response
            return {"response_data": res, "sql_data": {"sql": None}, "yaml_data": yaml_data,
                    "headers": headers, "cookie": cookie, "res_time": res_time, "status_code": status_code,
                    "teardown": teardown, "teardown_sql": teardown_sql}

    @classmethod
    def file_data_exit(cls, yaml_data, file_data):
        """判断上传文件时，data参数是否存在"""
        # 兼容又要上传文件，又要上传其他类型参数
        try:
            for key, value in yaml_data[YAMLDate.DATA.value]['data'].items():
                file_data[key] = value
        except KeyError:
            pass

    @classmethod
    def multipart_data(cls, file_data):
        multipart = MultipartEncoder(
            fields=file_data,  # 字典格式
            boundary='-----------------------------' + str(random.randint(int(1e28), int(1e29 - 1)))
        )
        return multipart

    @classmethod
    def check_headers_str_null(cls, headers):
        """
        兼容用户未填写headers或者header值为int
        @return:
        """
        headers = eval(cache_regular(str(headers)))
        if headers is None:
            return {"headers": None}
        else:
            for k, v in headers.items():
                if not isinstance(v, str):
                    headers[k] = str(v)
            return headers

    @classmethod
    def multipart_in_headers(cls, request_data, header):
        header = eval(cache_regular(str(header)))
        request_data = eval(cache_regular(str(request_data)))
        """ 判断处理header为 Content-Type: multipart/form-data"""
        if header is None:
            return request_data, {"headers": None}
        else:
            # 将header中的int转换成str
            for k, v in header.items():
                if not isinstance(v, str):
                    header[k] = str(v)
            if "multipart/form-data" in str(header.values()):
                # 判断请求参数不为空, 并且参数是字典类型
                if request_data and isinstance(request_data, dict):
                    # 当 Content-Type 为 "multipart/form-data"时，需要将数据类型转换成 str
                    for k, v in request_data.items():
                        if not isinstance(v, str):
                            request_data[k] = str(v)

                    request_data = MultipartEncoder(request_data)
                    header['Content-Type'] = request_data.content_type

        return request_data, header

    @classmethod
    def file_prams_exit(cls, yaml_data):
        # 判断上传文件接口，文件参数是否存在
        try:
            params = yaml_data[YAMLDate.DATA.value]['params']
        except KeyError:
            params = None
        return params

    @classmethod
    def text_encode(cls, text):
        """unicode 解码"""
        return text.encode("utf-8").decode("utf-8")
        # return text

    @classmethod
    def response_elapsed_total_seconds(cls, res):
        """获取接口响应时长"""
        try:
            return res.elapsed.total_seconds() * 1000
        except AttributeError:
            return 0.00

    @classmethod
    def upload_file(cls, yaml_data):
        """
        判断处理上传文件
        :param yaml_data:
        :return:
        """
        # 处理上传多个文件的情况
        yaml_data = eval(cache_regular(str(yaml_data)))
        _files = []
        file_data = {}
        # 兼容又要上传文件，又要上传其他类型参数
        cls.file_data_exit(yaml_data, file_data)
        for key, value in yaml_data[YAMLDate.DATA.value]['file'].items():
            file_path = ConfigHandler.file_path + value
            file_data[key] = (value, open(file_path, 'rb'), 'application/octet-stream')
            _files.append(file_data)
            # allure中展示该附件
            allure_attach(source=file_path, name=value, extension=value)
        multipart = cls.multipart_data(file_data)
        yaml_data[YAMLDate.HEADER.value]['Content-Type'] = multipart.content_type
        params_data = cls.file_prams_exit(yaml_data)
        return multipart, params_data, yaml_data

    @classmethod
    def get_response_cache(cls, response_cache, response_data, request_data):
        """
        将当前请求的接口存入缓存中
        @param response_cache: 设置缓存相关数据要求
        @param response_data: 接口相应内容
        @param request_data: 接口请求内容
        @return:
        """
        # 判断当前用例中如果有需要存入缓存的数据，才会进行下一步
        if response_cache is not None:
            _cache_name = response_cache['cache_name']
            _jsonpath = response_cache['jsonpath']
            _cache_type = response_cache['cache_type']
            _data = None
            if _cache_type == 'request':
                _data = jsonpath.jsonpath(obj=request_data, expr=_jsonpath)
            elif _cache_type == 'response':
                _data = jsonpath.jsonpath(obj=response_data, expr=_jsonpath)
            if _data is not False:
                Cache(_cache_name).set_caches(_data[0])
            else:
                ERROR.logger.error(f"缓存写入失败，接口返回数据 {response_cache} ，"
                                   f"接口请求数据 {request_data},"
                                   f"jsonpath内容：{response_cache}")

    @log_decorator(True)
    @execution_duration(3000)
    # @encryption("md5")
    def http_request(self, yaml_data, dependent_switch=True, **kwargs):
        """
        请求封装
        :param yaml_data: 从yaml文件中读取出来的所有数据
        :param dependent_switch:
        :param kwargs:
        :return:
        """
        from utils.requestsUtils.dependentCase import DependentCase
        _is_run = yaml_data[YAMLDate.IS_RUN.value]
        _method = yaml_data[YAMLDate.METHOD.value]
        _detail = yaml_data[YAMLDate.DETAIL.value]
        _headers = yaml_data[YAMLDate.HEADER.value]
        _requestType = yaml_data[YAMLDate.REQUEST_TYPE.value].upper()
        _data = yaml_data[YAMLDate.DATA.value]
        _sql = yaml_data[YAMLDate.SQL.value]
        _assert = yaml_data[YAMLDate.ASSERT.value]
        _dependent_data = yaml_data[YAMLDate.DEPENDENCE_CASE_DATA.value]
        _teardown = yaml_data[YAMLDate.TEARDOWN.value]
        _teardown_sql = yaml_data[YAMLDate.TEARDOWN_SQL.value]
        _current_request_set_cache = yaml_data[YAMLDate.CURRENT_REQUEST_SET_CACHE.value]
        _sleep = yaml_data[YAMLDate.SLEEP.value]
        _response_cache = yaml_data[YAMLDate.RESPONSE_CACHE.value]
        res = None

        # 判断用例是否执行
        if _is_run is True or _is_run is None:
            # 处理多业务逻辑
            if dependent_switch is True:
                DependentCase().get_dependent_data(yaml_data)

            if _requestType == RequestType.JSON.value:
                yaml_data = eval(cache_regular(str(yaml_data)))
                _headers = self.check_headers_str_null(_headers)
                _data = yaml_data[YAMLDate.DATA.value]

                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value], json=_data,
                                       headers=_headers, verify=False, **kwargs)
            elif _requestType == RequestType.NONE.value:
                yaml_data = eval(cache_regular(str(yaml_data)))
                _headers = self.check_headers_str_null(_headers)
                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value], data=None,
                                       headers=_headers, verify=False, **kwargs)

            elif _requestType == RequestType.PARAMS.value:
                yaml_data = eval(cache_regular(str(yaml_data)))
                _data = yaml_data[YAMLDate.DATA.value]
                url = yaml_data[YAMLDate.URL.value]
                if _data is not None:
                    # url 拼接的方式传参
                    params_data = "?"
                    for k, v in _data.items():
                        params_data += (k + "=" + str(v) + "&")
                    url = yaml_data[YAMLDate.URL.value] + params_data[:-1]
                _headers = self.check_headers_str_null(_headers)
                res = requests.request(method=_method, url=url, headers=_headers, verify=False, **kwargs)
            # 判断上传文件
            elif _requestType == RequestType.FILE.value:
                multipart = self.upload_file(yaml_data)
                yaml_data = multipart[2]
                _headers = multipart[2][YAMLDate.HEADER.value]
                _headers = self.check_headers_str_null(_headers)
                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value],
                                       data=multipart[0], params=multipart[1], headers=_headers, verify=False, **kwargs)

            elif _requestType == RequestType.DATA.value:
                yaml_data = eval(cache_regular(str(yaml_data)))
                _data, _headers = self.multipart_in_headers(_data, _headers)
                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value], data=_data, headers=_headers,
                                       verify=False, **kwargs)

            elif _requestType == RequestType.EXPORT.value:
                yaml_data = eval(cache_regular(str(yaml_data)))
                _headers = self.check_headers_str_null(_headers)
                _data = yaml_data[YAMLDate.DATA.value]
                res = requests.request(method=_method, url=yaml_data[YAMLDate.URL.value], json=_data, headers=_headers,
                                       verify=False, stream=False, **kwargs)
                content_disposition = res.headers.get('content-disposition')
                filename_code = content_disposition.split("=")[-1]  # 分隔字符串，提取文件名
                filename = urllib.parse.unquote(filename_code)  # url解码
                filepath = os.path.join(ConfigHandler.file_path, filename)  # 拼接路径
                if res.status_code == 200:
                    if res.text:  # 判断文件内容是否为空
                        with open(filepath, 'wb') as f:
                            for chunk in res.iter_content(chunk_size=1):  # iter_content循环读取信息写入，chunk_size设置文件大小
                                f.write(chunk)
                    else:
                        print("文件为空")
            if _sleep is not None:
                time.sleep(_sleep)
            _status_code = res.status_code
            allure_step_no(f"请求URL: {yaml_data[YAMLDate.URL.value]}")
            allure_step_no(f"请求方式: {_method}")
            allure_step("请求头: ", _headers)
            allure_step("请求数据: ", _data)
            allure_step("依赖数据: ", _dependent_data)
            allure_step("预期数据: ", _assert)
            _res_time = self.response_elapsed_total_seconds(res)
            allure_step_no(f"响应耗时(s): {_res_time}")
            try:
                res = res.json()
                allure_step("响应结果: ", res)
            except:
                if _requestType == RequestType.EXPORT.value:
                    res = filename
                else:
                    res = self.text_encode(res.text)
                    allure_step("响应结果: ", res)
            try:
                cookie = res.cookies.get_dict()
            except:
                cookie = None
            SetCurrentRequestCache(
                current_request_set_cache=_current_request_set_cache,
                request_data=yaml_data['data'],
                response_data=res
            ).set_caches_main()
            self.get_response_cache(response_cache=_response_cache, response_data=res, request_data=_data)
            return self._check_params(res, yaml_data, _headers, cookie, _res_time,
                                      _status_code, _teardown, _teardown_sql)
        else:
            # 用例跳过执行的话，响应数据和sql数据为空
            return {"response_data": False, "sql_data": False, "yaml_data": yaml_data, "res_time": 0.00}
