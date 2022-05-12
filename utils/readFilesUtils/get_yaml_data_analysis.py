#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/22 13:45
# @Author : 余少琪

from utils.otherUtils.get_conf_data import sql_switch
from utils.readFilesUtils.yamlControl import GetYamlData


class CaseData:
    """
    yaml 数据解析, 判断数据填写是否符合规范
    """

    def __init__(self, file_path):
        self.filePath = file_path

    def case_process(self, case_id_switch=None):
        """
        数据清洗之后，返回该 yaml 文件中的所有用例
        :param case_id_switch: 判断数据清洗，是否需要清洗出 case_id, 主要用于兼容用例池中的数据
        :return:
        """
        dates = GetYamlData(self.filePath).get_yaml_data()
        case_lists = []
        for key, values in dates.items():
            # 公共配置中的数据，与用例数据不同，需要单独处理
            if key != 'case_common':
                case_date = {
                    'method': self.get_case_method(case_id=key, case_data=values),
                    'is_run': self.get_is_run(key, values),
                    'url': self.get_case_host(case_id=key, case_data=values),
                    'detail': self.get_case_detail(case_id=key, case_data=values),
                    'headers': self.get_headers(case_id=key, case_data=values, file_path=self.filePath),
                    'requestType': self.get_request_type(key, values),
                    'data': self.get_case_dates(key, values),
                    'dependence_case': self.get_dependence_case(key, values),
                    'dependence_case_data': self.get_dependence_case_data(key, values),
                    "sql": self.get_sql(key, values),
                    "assert": self.get_assert(key, values),
                    "setup_sql": self.setup_sql(values)
                }

                if case_id_switch is True:
                    case_lists.append({key: case_date})
                else:
                    # 正则处理，如果用例中有需要读取缓存中的数据，则优先读取缓存

                    case_lists.append(case_date)
        return case_lists

    def get_case_host(self, case_id: str, case_data: dict) -> str:
        """
        获取用例的 host
        :return:
        """
        try:
            _url = case_data['url']
            _host = case_data['host']
            if _url is None or _host is None:
                raise ValueError(f"用例中的 url 或者 host 不能为空！\n 用例ID: {case_id} \n 用例路径: {self.filePath}")
            else:
                return _host + _url
        except KeyError:
            raise KeyError(self.raise_value_null_error(data_name="url 或 host", case_id=case_id))

    def get_case_method(self, case_id: str, case_data: dict) -> str:
        """
        获取用例的请求方式：GET/POST/PUT/DELETE
        :return:
        """
        try:
            _case_method = case_data['method']
            _request_method = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTION']
            if _case_method.upper() in _request_method:
                return _case_method.upper()
            else:
                raise ValueError(f"method 目前只支持 {_request_method} 请求方式，如需新增请联系管理员. "
                                 f"{self.raise_value_error(data_name='请求方式', case_id=case_id, detail=_case_method)}")

        except AttributeError:
            raise ValueError(f"method 目前只支持 { ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTION']} 请求方式，"
                             f"如需新增请联系管理员！ "
                             f"{self.raise_value_error(data_name='请求方式', case_id=case_id, detail=case_data['method'])}")
        except KeyError:
            raise KeyError(self.raise_value_null_error(data_name="method", case_id=case_id))

    def get_case_detail(self, case_id, case_data: dict) -> str:
        """
        获取用例描述
        :return:
        """
        try:
            return case_data['detail']
        except KeyError:
            raise KeyError(self.raise_value_null_error(case_id=case_id, data_name="detail"))

    def get_headers(self, case_id: str, case_data: dict, file_path: str) -> dict:
        """
        胡求用例请求头中的信息
        :return:
        """
        try:
            _header = case_data['headers']
            return _header
        except KeyError:
            raise KeyError(self.raise_value_null_error(case_id=case_id, data_name="headers"))

    def raise_value_error(self, data_name: str, case_id: str, detail: [str, list, dict]):
        """
        所有用例填写不规范的异常提示
        :param data_name: 参数名称
        :param case_id: 用例ID
        :param detail: 参数内容
        :return:
        """
        detail = f"用例中的 {data_name} 填写不正确！\n 用例ID: {case_id} \n 用例路径: {self.filePath}\n" \
                 f"当前填写的内容: {detail}"

        return detail

    def raise_value_null_error(self, data_name: str, case_id: str):
        """
        用例中参数名称为空的异常提示
        :param data_name: 参数名称
        :param case_id: 用例ID
        :return:
        """
        detail = f"用例中未找到 {data_name} 参数， 如已填写，请检查用例缩进是否存在问题" \
                 f"用例ID: {case_id} " \
                 f"用例路径: {self.filePath}"

        return detail

    def get_request_type(self, case_id: str, case_data: dict) -> str:
        """
        获取请求类型，params、data、json
        :return:
        """

        _types = ['JSON', 'PARAMS', 'FILE', 'DATE']

        try:
            _request_type = case_data['requestType']
            # 判断用户填写的 requestType是否符合规范
            if _request_type.upper() in _types:
                return _request_type.upper()
            else:
                raise ValueError(self.raise_value_error(data_name='requestType', case_id=case_id, detail=_request_type))
        # 异常捕捉
        except AttributeError:
            raise ValueError(self.raise_value_error(data_name='requestType',
                                                    case_id=case_id, detail=case_data['requestType']))
        except KeyError:
            raise KeyError(self.raise_value_null_error(case_id=case_id, data_name="requestType"))

    def get_is_run(self, case_id: str, case_data: dict) -> str:
        """
        获取执行状态, 为 true 或者 None 都会执行
        :return:
        """
        try:
            return case_data['is_run']
        except KeyError:
            raise KeyError(self.raise_value_null_error(case_id=case_id, data_name="is_run"))

    def get_dependence_case(self, case_id: str, case_data: dict) -> dict:
        """
        获取是否依赖的用例
        :return:
        """
        try:
            _dependence_case = case_data['dependence_case']
            return _dependence_case
        except KeyError:
            raise KeyError(self.raise_value_null_error(case_id=case_id, data_name="dependence_case"))

    # TODO 对 dependence_case_data 中的值进行验证
    def get_dependence_case_data(self, case_id: str, case_data: dict) -> dict:
        """
        获取依赖的用例
        :return:
        """
        # 判断如果该用例有依赖，则返回依赖数据，否则返回None
        if self.get_dependence_case(case_id=case_id, case_data=case_data):
            try:
                _dependence_case_data = case_data['dependence_case_data']
                # 判断当用例中设置的需要依赖用例，但是dependence_case_data下方没有填写依赖的数据，异常提示
                if _dependence_case_data is None:
                    raise ValueError(f"dependence_case_data 依赖数据中缺少依赖相关数据！"
                                     f"如有填写，请检查缩进是否正确"
                                     f"用例ID: {case_id}"
                                     f"用例路径: {self.filePath}")

                return _dependence_case_data
            except KeyError:
                raise KeyError(self.raise_value_null_error(case_id=case_id, data_name="dependence_case_data"))
        else:
            return {"dependence_case_data": None}

    def get_case_dates(self, case_id: str, case_data: dict) -> dict:
        """
        获取请求数据
        :param case_id:
        :param case_data:
        :return:
        """
        try:
            _dates = case_data['data']
            return _dates
        except KeyError:
            raise KeyError(self.raise_value_null_error(case_id=case_id, data_name="data"))

    # TODO 对 assert 中的值进行验证
    def get_assert(self, case_id: str, case_data: dict):
        """
        获取需要断言的数据
        :return:
        """
        try:
            _assert = case_data['assert']
            if _assert is None:
                raise self.raise_value_error(data_name="assert", case_id=case_id, detail=_assert)
            return case_data['assert']
        except KeyError:
            raise KeyError(self.raise_value_null_error(case_id=case_id, data_name="assert"))

    def get_sql(self, case_id: str, case_data: dict):
        """
        获取测试用例中的断言sql
        :return:
        """
        try:
            _sql = case_data['sql']
            # 判断数据库开关为开启状态，并且sql不为空
            if sql_switch() and _sql is not None:
                return case_data['sql']
            else:
                return None
        except KeyError:
            raise KeyError(self.raise_value_null_error(case_id=case_id, data_name="sql"))

    @classmethod
    def setup_sql(cls, case_data: dict):
        """
        获取前置sql，比如该条用例中需要从数据库中读取sql作为用例参数，则需填写setup_sql
        :return:
        """
        try:
            _setup_sql = case_data['setup_sql']
            return _setup_sql
        except KeyError:
            return None
