#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 12:52
# @Author : 余少琪
"""
import os
import random
import time
import urllib
from typing import Tuple, Dict, Union, Text
import requests
import urllib3
from requests_toolbelt import MultipartEncoder
from Enums.requestType_enum import RequestType
from Enums.yamlData_enum import YAMLDate
from common.setting import ConfigHandler
from utils.logging_tool.log_decorator import log_decorator
from utils.mysql_tool.mysql_control import MysqlDB
from utils.other_tools.get_conf_data import sql_switch
from utils.logging_tool.run_time_decorator import execution_duration
from utils.other_tools.allure_data.allure_tools import allure_step, allure_step_no, allure_attach
from utils.read_files_tools.regular_control import cache_regular
from utils.requests_tool.set_current_request_cache import SetCurrentRequestCache
from utils.requests_tool.encryption_algorithm_control import encryption

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
        """ 处理上传文件数据 """
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
            for key, value in headers.items():
                if not isinstance(value, str):
                    headers[key] = str(value)
            return headers

    @classmethod
    def multipart_in_headers(
            cls,
            request_data: Dict,
            header: Dict):
        """ 判断处理header为 Content-Type: multipart/form-data"""
        header = eval(cache_regular(str(header)))
        request_data = eval(cache_regular(str(request_data)))

        if header is None:
            return request_data, {"headers": None}
        else:
            # 将header中的int转换成str
            for key, value in header.items():
                if not isinstance(value, str):
                    header[key] = str(value)
            if "multipart/form-data" in str(header.values()):
                # 判断请求参数不为空, 并且参数是字典类型
                if request_data and isinstance(request_data, dict):
                    # 当 Content-Type 为 "multipart/form-data"时，需要将数据类型转换成 str
                    for key, value in request_data.items():
                        if not isinstance(value, str):
                            request_data[key] = str(value)

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

    def request_type_for_json(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: Text,
            data: Union[Dict, None],
            **kwargs):
        """ 判断请求类型为json格式 """
        yaml_data = eval(cache_regular(str(yaml_data)))
        _headers = self.check_headers_str_null(headers)
        _data = yaml_data[YAMLDate.DATA.value]

        res = requests.request(
            method=method,
            url=yaml_data[YAMLDate.URL.value],
            json=_data,
            data=data,
            headers=_headers,
            verify=False,
            params=None,
            **kwargs
        )
        return res, yaml_data

    def request_type_for_none(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: Text,
            data: Union[Dict, None],
            **kwargs) -> object:
        """判断 requestType 为 None"""
        yaml_data = eval(cache_regular(str(yaml_data)))
        _headers = self.check_headers_str_null(headers)
        res = requests.request(
            method=method,
            url=yaml_data[YAMLDate.URL.value],
            data=data,
            headers=_headers,
            verify=False,
            params=None,
            **kwargs
        )
        return res, yaml_data

    def request_type_for_params(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: Text,
            data: Union[Dict, None],
            **kwargs):

        """处理 requestType 为 params """
        yaml_data = eval(cache_regular(str(yaml_data)))
        _data = yaml_data[YAMLDate.DATA.value]
        url = yaml_data[YAMLDate.URL.value]
        if _data is not None:
            # url 拼接的方式传参
            params_data = "?"
            for key, value in _data.items():
                if value is None or value == '':
                    params_data += (key + "&")
                else:
                    params_data += (key + "=" + str(value) + "&")
            url = yaml_data[YAMLDate.URL.value] + params_data[:-1]
        _headers = self.check_headers_str_null(headers)
        res = requests.request(
            method=method,
            url=url,
            headers=_headers,
            verify=False,
            data=data,
            params=None,
            **kwargs)
        return res, yaml_data

    def request_type_for_file(
            self,
            yaml_data: Dict,
            method: Text,
            data: Union[Dict, None],
            headers: Union[Dict, None],
            **kwargs):
        """处理 requestType 为 file 类型"""
        multipart = self.upload_file(yaml_data)
        yaml_data = multipart[2]
        _headers = multipart[2][YAMLDate.HEADER.value]
        _headers = self.check_headers_str_null(_headers)
        res = requests.request(
            method=method,
            url=yaml_data[YAMLDate.URL.value],
            data=multipart[0],
            params=multipart[1],
            headers=_headers,
            verify=False,
            **kwargs
        )
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
        res = requests.request(
            method=method,
            url=yaml_data[YAMLDate.URL.value],
            data=_data,
            headers=_headers,
            verify=False,
            **kwargs)

        return res, yaml_data

    @classmethod
    def get_export_api_filename(cls, res):
        """ 处理导出文件 """
        content_disposition = res.headers.get('content-disposition')
        filename_code = content_disposition.split("=")[-1]  # 分隔字符串，提取文件名
        filename = urllib.parse.unquote(filename_code)  # url解码
        return filename

    def request_type_for_export(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: Text,
            data: Union[None, Dict],
            **kwargs):
        """判断 requestType 为 export 导出类型"""
        yaml_data = eval(cache_regular(str(yaml_data)))
        _headers = self.check_headers_str_null(headers)
        _data = yaml_data[YAMLDate.DATA.value]
        res = requests.request(
            method=method,
            url=yaml_data[YAMLDate.URL.value],
            json=_data,
            headers=_headers,
            verify=False,
            stream=False,
            data=data,
            **kwargs)
        filepath = os.path.join(ConfigHandler.file_path, self.get_export_api_filename(res))  # 拼接路径
        if res.status_code == 200:
            if res.text:  # 判断文件内容是否为空
                with open(filepath, 'wb') as file:
                    # iter_content循环读取信息写入，chunk_size设置文件大小
                    for chunk in res.iter_content(chunk_size=1):
                        file.write(chunk)
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
            # 这个用于日志专用，判断如果是get请求，直接打印url
            "request_body": self._request_body_handler(
                yaml_data[YAMLDate.DATA.value], res.request.method
            ),
            "method": res.request.method,
            "sql_data": self._sql_data_handler(sql_data=yaml_data[YAMLDate.SQL.value], res=res),
            "yaml_data": yaml_data,
            "headers": res.request.headers,
            "cookie": res.cookies,
            "assert": yaml_data[YAMLDate.ASSERT.value],
            "res_time": self.response_elapsed_total_seconds(res),
            "status_code": res.status_code,
            "teardown": yaml_data[YAMLDate.TEARDOWN.value],
            "teardown_sql": yaml_data[YAMLDate.TEARDOWN_SQL.value],
            "body": yaml_data[YAMLDate.DATA.value]
        }
        # 抽离出通用模块，判断 http_request 方法中的一些数据校验
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
    @encryption("md5")
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
        from utils.requests_tool.dependent_case import DependentCase
        _is_run = yaml_data[YAMLDate.IS_RUN.value]
        _method = yaml_data[YAMLDate.METHOD.value]
        _headers = yaml_data[YAMLDate.HEADER.value]
        _request_type = yaml_data[YAMLDate.REQUEST_TYPE.value].upper()
        _data = yaml_data[YAMLDate.DATA.value]
        _current_request_set_cache = yaml_data[YAMLDate.CURRENT_REQUEST_SET_CACHE.value]
        _sleep = yaml_data[YAMLDate.SLEEP.value]

        requests_type_mapping = {
            RequestType.JSON.value: self.request_type_for_json,
            RequestType.NONE.value: self.request_type_for_none,
            RequestType.PARAMS.value: self.request_type_for_params,
            RequestType.FILE.value: self.request_type_for_file,
            RequestType.DATA.value:  self.request_type_for_data,
            RequestType.EXPORT.value: self.request_type_for_export
        }

        # 判断用例是否执行
        if _is_run is True or _is_run is None:
            # 处理多业务逻辑
            if dependent_switch is True:
                DependentCase().get_dependent_data(yaml_data)

            res, yaml_data = requests_type_mapping.get(_request_type)(
                yaml_data=yaml_data,
                headers=_headers,
                method=_method,
                data=_data,
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
                data=_res_data['body'],
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

            return _res_data
