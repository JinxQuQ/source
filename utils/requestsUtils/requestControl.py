#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 12:52
# @Author : 余少琪
import copy
import os
import random
import time
import urllib
import jsonpath
import requests
import urllib3
from typing import Tuple, Dict, Union, Text
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
    def file_data_exit(
            cls,
            yaml_data: Dict,
            file_data) -> None:
        """判断上传文件时，data参数是否存在"""
        # 兼容又要上传文件，又要上传其他类型参数
        try:
            for key, value in yaml_data[YAMLDate.DATA.value]['data'].items():
                file_data[key] = value
        except KeyError:
            ...

    @classmethod
    def multipart_data(
            cls,
            file_data: Dict):
        multipart = MultipartEncoder(
            fields=file_data,  # 字典格式
            boundary='-----------------------------' + str(random.randint(int(1e28), int(1e29 - 1)))
        )
        return multipart

    @classmethod
    def check_headers_str_null(
            cls,
            headers: Dict) -> Dict:
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
    def multipart_in_headers(
            cls,
            request_data: Dict,
            header: Dict):
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
    def file_prams_exit(
            cls,
            yaml_data: Dict) -> Dict:
        """判断上传文件接口，文件参数是否存在"""
        try:
            params = yaml_data[YAMLDate.DATA.value]['params']
        except KeyError:
            params = None
        return params

    @classmethod
    def text_encode(
            cls,
            text: Text) -> Text:
        """unicode 解码"""
        return text.encode("utf-8").decode("utf-8")
        # return text

    @classmethod
    def response_elapsed_total_seconds(
            cls,
            res) -> float:
        """获取接口响应时长"""
        try:
            return round(res.elapsed.total_seconds() * 1000, 2)
        except AttributeError:
            return 0.00

    @classmethod
    def upload_file(
            cls,
            yaml_data: Dict) -> Tuple:
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
    def get_response_cache(
            cls,
            response_cache: Dict,
            response_data: Dict,
            request_data: Dict) -> None:
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
                _data = jsonpath.jsonpath(
                    obj=request_data,
                    expr=_jsonpath
                )
            elif _cache_type == 'response':
                _data = jsonpath.jsonpath(
                    obj=response_data,
                    expr=_jsonpath
                )
            if _data is not False:
                Cache(_cache_name).set_caches(_data[0])
            else:
                ERROR.logger.error(f"缓存写入失败，接口返回数据 {response_cache} ，"
                                   f"接口请求数据 {request_data},"
                                   f"jsonpath内容：{response_cache}")

    def request_type_for_json(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: Text,
            **kwargs):
        """ 判断请求类型为json格式 """
        yaml_data = eval(cache_regular(str(yaml_data)))
        _headers = self.check_headers_str_null(headers)
        _data = yaml_data[YAMLDate.DATA.value]

        res = requests.request(
            method=method,
            url=yaml_data[YAMLDate.URL.value],
            json=_data,
            headers=_headers,
            verify=False,
            **kwargs
        )
        return res, yaml_data

    def request_type_for_none(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: Text,
            **kwargs) -> object:
        """判断 requestType 为 None"""
        yaml_data = eval(cache_regular(str(yaml_data)))
        _headers = self.check_headers_str_null(headers)
        res = requests.request(
            method=method,
            url=yaml_data[YAMLDate.URL.value],
            data=None,
            headers=_headers,
            verify=False,
            **kwargs
        )
        return res, yaml_data

    def request_type_for_params(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: Text,
            **kwargs):

        """处理 requestType 为 params """
        yaml_data = eval(cache_regular(str(yaml_data)))
        _data = yaml_data[YAMLDate.DATA.value]
        url = yaml_data[YAMLDate.URL.value]
        if _data is not None:
            # url 拼接的方式传参
            params_data = "?"
            for k, v in _data.items():
                if v is None or v == '':
                    params_data += (k + "&")
                else:
                    params_data += (k + "=" + str(v) + "&")
            url = yaml_data[YAMLDate.URL.value] + params_data[:-1]
        _headers = self.check_headers_str_null(headers)
        res = requests.request(method=method, url=url, headers=_headers, verify=False, **kwargs)
        return res, yaml_data

    def request_type_for_file(
            self,
            yaml_data: Dict,
            method: Text,
            **kwargs):
        """处理 requestType 为 file 类型"""
        multipart = self.upload_file(yaml_data)
        yaml_data = multipart[2]
        _headers = multipart[2][YAMLDate.HEADER.value]
        _headers = self.check_headers_str_null(_headers)
        res = requests.request(method=method, url=yaml_data[YAMLDate.URL.value],
                               data=multipart[0], params=multipart[1], headers=_headers, verify=False, **kwargs)
        return res, yaml_data

    def request_type_for_data(
            self,
            yaml_data: Dict,
            data: Dict,
            headers: Dict,
            method: Text,
            **kwargs):
        """判断 requestType 为 data 类型"""
        yaml_data = eval(cache_regular(str(yaml_data)))
        _data, _headers = self.multipart_in_headers(data, headers)
        res = requests.request(method=method, url=yaml_data[YAMLDate.URL.value], data=_data, headers=_headers,
                               verify=False, **kwargs)

        return res, yaml_data

    @classmethod
    def get_export_api_filename(cls, res):
        content_disposition = res.headers.get('content-disposition')
        filename_code = content_disposition.split("=")[-1]  # 分隔字符串，提取文件名
        filename = urllib.parse.unquote(filename_code)  # url解码
        return filename

    def request_type_for_export(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: Text,
            **kwargs):
        """判断 requestType 为 export 导出类型"""
        yaml_data = eval(cache_regular(str(yaml_data)))
        _headers = self.check_headers_str_null(headers)
        _data = yaml_data[YAMLDate.DATA.value]
        res = requests.request(method=method, url=yaml_data[YAMLDate.URL.value], json=_data, headers=_headers,
                               verify=False, stream=False, **kwargs)
        filepath = os.path.join(ConfigHandler.file_path, self.get_export_api_filename(res))  # 拼接路径
        if res.status_code == 200:
            if res.text:  # 判断文件内容是否为空
                with open(filepath, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=1):  # iter_content循环读取信息写入，chunk_size设置文件大小
                        f.write(chunk)
            else:
                print("文件为空")

        return res, yaml_data

    @classmethod
    def _request_body_handler(cls, data: Dict, method: Text) -> Union[None, Dict]:
        """处理请求参数 """
        if method.upper() == 'GET':
            return None
        else:
            return data

    @classmethod
    def _sql_data_handler(cls, sql_data, res):
        """处理 sql 参数 """
        # 判断数据库开关，开启状态，则返回对应的数据
        if sql_switch() and sql_data is not None:
            sql_data = MysqlDB().assert_execution(
                sql=sql_data,
                resp=res.json()
            )

        else:
            sql_data = {"sql": None}
        return sql_data

    def _check_params(
            self,
            res,
            yaml_data: Dict,
    ) -> Dict:

        _data = {
            "url": res.url,
            "is_run": yaml_data[YAMLDate.IS_RUN.value],
            "detail": yaml_data[YAMLDate.DETAIL.value],
            "response_data": res.text,
            "request_body": self._request_body_handler(yaml_data[YAMLDate.DATA.value], res.request.method),
            "method": res.request.method,
            "sql_data": self._sql_data_handler(sql_data=yaml_data[YAMLDate.SQL.value], res=res),
            "yaml_data": yaml_data,
            "headers": res.request.headers,
            "cookie": res.cookies,
            "assert": yaml_data[YAMLDate.ASSERT.value],
            "res_time": self.response_elapsed_total_seconds(res),
            "status_code": res.status_code,
            "teardown": yaml_data[YAMLDate.TEARDOWN.value],
            "teardown_sql": yaml_data[YAMLDate.TEARDOWN_SQL.value]
        }
        """ 抽离出通用模块，判断 http_request 方法中的一些数据校验 """
        return _data

    @classmethod
    def api_allure_step(
            cls,
            headers: Text,
            method: Text,
            data: Text,
            assert_data: Text,
            status_code: Text,
            res_time: Text
    ) -> None:
        """ 在allure中记录请求数据 """
        _status_code = str(status_code)
        allure_step_no(f"请求方式: {method}")
        allure_step("请求头: ", headers)
        allure_step("请求数据: ", data)
        allure_step("预期数据: ", assert_data)
        _res_time = res_time
        allure_step_no(f"响应耗时(ms): {str(_res_time)}")

    @log_decorator(True)
    @execution_duration(3000)
    # @encryption("md5")
    def http_request(
            self,
            yaml_data: Dict,
            dependent_switch=True,
            **kwargs
    ):
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
        _headers = yaml_data[YAMLDate.HEADER.value]
        _requestType = yaml_data[YAMLDate.REQUEST_TYPE.value].upper()
        _data = yaml_data[YAMLDate.DATA.value]
        _current_request_set_cache = yaml_data[YAMLDate.CURRENT_REQUEST_SET_CACHE.value]
        _sleep = yaml_data[YAMLDate.SLEEP.value]
        _response_cache = yaml_data[YAMLDate.RESPONSE_CACHE.value]
        res = None

        # 判断用例是否执行
        if _is_run is True or _is_run is None:
            # 处理多业务逻辑
            if dependent_switch is True:
                DependentCase().get_dependent_data(yaml_data)
            # 判断请求类型为json形式的
            if _requestType == RequestType.JSON.value:
                res,  yaml_data = self.request_type_for_json(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    **kwargs
                )
            elif _requestType == RequestType.NONE.value:
                res, yaml_data = self.request_type_for_none(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    **kwargs
                )

            elif _requestType == RequestType.PARAMS.value:
                res, yaml_data = self.request_type_for_params(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    **kwargs
                )
            # 判断上传文件
            elif _requestType == RequestType.FILE.value:
                res, yaml_data = self.request_type_for_file(
                    yaml_data=yaml_data,
                    method=_method,
                    **kwargs
                )

            elif _requestType == RequestType.DATA.value:
                res, yaml_data = self.request_type_for_data(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    data=_data,
                    **kwargs
                )

            elif _requestType == RequestType.EXPORT.value:
                res, yaml_data = self.request_type_for_export(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    **kwargs
                )

            if _sleep is not None:
                time.sleep(_sleep)

            _res_data = self._check_params(
                res=res,
                yaml_data=yaml_data)

            self.api_allure_step(
                headers=_res_data['headers'],
                method=_res_data['method'],
                data=_res_data['request_body'],
                assert_data=_res_data['assert'],
                res_time=_res_data['res_time'],
                status_code=_res_data['status_code']
            )
            # 将当前请求数据存入缓存中
            SetCurrentRequestCache(
                current_request_set_cache=_current_request_set_cache,
                request_data=yaml_data['data'],
                response_data=res
            ).set_caches_main()

            # 获取当前请求的缓存
            self.get_response_cache(
                response_cache=_response_cache,
                response_data=res,
                request_data=_data)
            return _res_data
        else:
            # 用例跳过执行的话，响应数据和sql数据为空
            _response_data = {
                "response_data": False,
                "sql_data": False,
                "yaml_data": yaml_data,
                "res_time": 0.00
            }
            return _response_data
