#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/6/22 10:26
# @Author : 余少琪

import random
import string
import datetime
import os
import copy
from ruamel import yaml
from enum import Enum
from utils.mysql_tool.mysql_control import MysqlDB
from utils.read_files_tools.yaml_control import GetYamlData
from common.setting import ConfigHandler
from utils.logging_tool.log_control import WARNING

# 枚举开关
_filed_enum_switch = True
_slash = os.sep


class FiledType(Enum):
    """
    field_type枚举 ，对应数据库t_open_field_cfg表中的 field_type枚举
    """
    int = '1'
    String = '2'
    date = '3'
    Time = '4'
    Timestamp = '5'
    decimal = '6'
    float = '7'
    double = '8'
    boolean = '9'
    long = '10'
    short = '11'
    enum = '12'


class GenerateCaseDate(MysqlDB):
    """根据模板自动生成测试用例数据"""

    def __init__(self):
        super().__init__()
        self._template_file_path = ConfigHandler.common_path + 'generate_case_template.yaml'
        self._data_path = ConfigHandler.data_path
        self.num = 1

    def get_template_data(self):
        """
        获取模板中的数据
        @return:
        """
        _case_data = GetYamlData(self._template_file_path).get_yaml_data()
        return _case_data['template_case']

    def get_bank_code(self, path_switch=False):
        """
        获取 url 中的 code码, 取前三位
        @param path_switch: 这个参数不判断是否存在银行,直接获取路径中的内容,作用于自动生成用例文件
        @return:
        """
        _host = self.get_template_data()['host']
        _url = _host + self.get_template_data()['url']
        # 存储所有银行code的列表，后续如有新的bank_code, 可以往这里加
        # 如果你们公司数据库中有这些数据的话，可以直接数据库中查
        bank_code_list = [
            'ABC', 'BBJ', 'BCM', 'BHX', 'BJS', 'BOC', 'BSH', 'CCB', 'CCT', 'CEB',
            'CGB', 'CIB', 'CMB', 'CMC', 'CZB', 'GZB', 'HXB', 'HZB', 'ICB', 'NBB',
            'NJB', 'PDB', 'PSB', 'SDB', 'ZJN'
        ]
        _url_bank_code = _url.split("/")[-2][:3]

        if _url_bank_code in bank_code_list or path_switch:
            return _url_bank_code
        else:
            return None

    def get_business_type(self):
        """
        获取 businessType
        @return:
        """
        _business_type = self.get_template_data()['data']['request']['requestHead']['businessType']
        return _business_type

    @classmethod
    def param_analysis(cls, data, sql_data):
        """
        参数解析，将数据库数据解析成字典
        @param sql_data:
        @param data:
        @return:
        """
        for i in data:
            sql_data[i['field_name']] = {
                "field_type": i['field_type'],
                "field_enums": i['field_enums'],
                "field_length": i['field_length'],
                "is_necessary": i['is_necessary'],
            }
        return sql_data

    def get_file_name(self):
        """
        获取url中的最后一个参数,作用于生成用例的文件名称
        @return:
        """
        _file_name = self.get_template_data()['url'].split("/")[-1]
        return _file_name

    def get_case_id(self):
        """
        获取case_id, 根据url中的后两位生成
        /openApi/business/YC000042/NBB01/pay --> NBB01_pay
        @return:
        """
        _url = self.get_template_data()['url'].split("/")
        case_id = _url[-2] + '_' + _url[-1]
        return case_id

    def get_request_head(self):
        """"获取 request_head """
        _request_head = self.get_template_data()['data']['request']['requestHead']
        return _request_head

    def get_sql_params(self):
        """
        根据模板中的接口，提取出数据库中的参数内容
        @return:
        """
        _sql_data = {}
        if self.get_bank_code() is not None:
            # 特有参数
            _unique_params = self.query(
                sql=f"SELECT * FROM t_open_field_cfg  "
                    f"where business_type = '{self.get_business_type()}' "
                    f"and bank_code = '{self.get_bank_code()}';"
            )
            self.param_analysis(data=_unique_params, sql_data=_sql_data)
        # 共有参数
        _common_params = self.query(
            "SELECT * FROM t_open_field_cfg  "
            f"where business_type = '{self.get_business_type()}' "
            "and (ISNULL(bank_code) || bank_code = '')"
        )
        _sql_data = self.param_analysis(data=_common_params, sql_data=_sql_data)
        return _sql_data

    def get_request_body(self):
        """
        获取测试用例的请求参数
        @return:
        """
        _request_body = self.get_template_data()['data']['request']['requestBody']
        return _request_body

    @classmethod
    def random_str(cls, length=16):
        """
        随机生成字符串
        @param length: 自定义字符串长度
        @return:
        """
        b = []
        for i in range(length):
            # 获取随机字符
            str_list = random.choice(string.digits + string.ascii_letters)
            # 将获得的随机字符添加到列表的末尾
            b.append(str_list)
        # 将获得的16个元素的列表，连接到字符串中，生成16位随机字符串
        random_str = ''.join(b)
        return random_str

    @classmethod
    def yaml_cases(cls, path, data: dict) -> None:
        """
        写入 yaml 数据

        @param data:
        @param path:
        """
        with open(path, "a", encoding="utf-8") as f:
            yaml.dump(data, f, Dumper=yaml.RoundTripDumper, allow_unicode=True)
            f.write('\n')

    @classmethod
    def get_now_time(cls):
        """
        生成当前时间
        @return:
        """
        _now_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return _now_time

    @classmethod
    def get_decimal_number(cls, min_num, max_num):
        """
        随机生成浮点数, 保留浮点数两位
        @param min_num: 随机生成的最小值
        @param max_num: 随机生成的最大值
        @return: 99.57
        """
        ret = round(random.uniform(min_num, max_num), 2)
        return ret

    @classmethod
    def _assert_data(cls, jsonpath, types, value, assert_type=None):
        """
        处理 assert_断言
        @return:
        """
        _assert_data = {
            "retMsg": {
                "jsonpath": jsonpath,
                "type": types,
                "value": value,
                "AssertType": assert_type
            }
        }
        return _assert_data

    def write_new_case_data(self, key, value, detail, assert_data):
        """处理数据之后，将用例写入 yaml """
        request_body = GetYamlData(self._template_file_path)\
            .get_yaml_data()['template_case']['data']['request']['requestBody']

        _request_body2 = self.get_request_body()

        self.replace_key(key, value, request_body, detail)
        _case_id = self.get_case_id() + str(self.num)
        _case_data = {_case_id: self.get_template_data()}
        _case_data[_case_id]['data']['request'] = {"requestHead": self.get_request_head(), "requestBody": request_body}
        _case_data[_case_id]['detail'] = detail
        _case_data[_case_id]['assert'] = assert_data

        # 存放测试用例路径
        _dir_path = self._data_path + self.get_bank_code(path_switch=True) + _slash
        _case_path = _dir_path + self.get_file_name() + '.yaml'
        if not os.path.exists(_dir_path):
            os.mkdir(_dir_path)

        _case_common = {
                "case_common": {"allureEpic": "NCBC", "allureFeature": self.get_bank_code(),
                                "allureStory": self.get_file_name()}
            }

        if not os.path.exists(_case_path):
            self.yaml_cases(data=_case_common, path=_case_path)
        self.yaml_cases(data=_case_data, path=_case_path)
        self.num += 1

    def replace_key(self, key, value, request_body: dict, detail):
        """
        根据数据类型条件，生成新的数据，替换模板中的内容
        @param key: 参数的键
        @param value: 需要生成的参数值
        @param request_body: 请求参数中的 request_body
        @param detail: 用例描述
        @return:
        """
        if isinstance(request_body, dict):
            if key in request_body:
                request_body[key] = value
            else:
                for k, v in request_body.items():
                    self.replace_key(key, value, v, detail)
        elif isinstance(request_body, list):
            for i in request_body:
                self.replace_key(key, value, i, detail)

    def field_length_generation_case(self, key, field_length):
        """
        根据长度自动生成用例
        @param key: 参数的键
        @param field_length: 长度长度
        @return:
        """
        # 自动生成字符串长度刚好等于数据长度
        self.write_new_case_data(
            key=key,
            value=self.random_str(length=int(field_length)),
            detail=f"测试参数{key}的长度刚好等于{field_length}",
            assert_data=self._assert_data(jsonpath="$.responseBody.result.returnCode", types="contains", value='000000'),
        )
        # 自动生成字符串长度大于数据库长度的用例
        self.write_new_case_data(
            key=key,
            value=self.random_str(length=int(field_length) + 1),
            detail=f"测试参数{key}的长度大于{field_length}",
            assert_data=self._assert_data(jsonpath="$.responseBody.result.retMsg", types="contains", value='OPEN358')
        )

        # 自动生成字符串长度小于数据库长度的用例
        self.write_new_case_data(
            key=key,
            value=self.random_str(length=int(field_length) - 1),
            detail=f"测试参数{key}的长度小于{field_length}",
            assert_data=self._assert_data(jsonpath="$.responseBody.result.returnCode", types="contains", value='000000'),
        )

    def filed_type_enums(self, key, enums):
        """
        判断根据参数的枚举自动生成数据
        @return:
        """
        self.write_new_case_data(
            key=key,
            value=enums,
            detail=f"测试{key}参数的枚举值，当前枚举{enums}",
            assert_data=self._assert_data(jsonpath="$.responseBody.result.returnCode", types="contains", value='000000'),
        )

    def filed_type_timestamp(self, key):
        """
        判断参数为
        @param key:
        @return:
        """
        self.write_new_case_data(
            key=key,
            value=self.get_now_time(),
            detail=f"测试{key}时间，自动生成当前时间",
            assert_data=self._assert_data(jsonpath="$.responseBody.result.returnCode", types="contains", value='000000'),
        )

    def filed_type_decimal(self, key):
        """ 处理自动生成 decimal 数据类型的用例 """
        self.write_new_case_data(
            key=key,
            # 数据范围可自定义，目前定义的是1-100中间值，随机生成浮点数
            value=self.get_decimal_number(1, 100),
            detail=f"测试{key}参数类型为 decimal，随机生成浮点数",
            assert_data=self._assert_data(jsonpath="$.responseBody.result.returnCode", types="contains", value='000000'),
        )

    def filed_is_necessary(self, key):
        """测试判断是否参数是否必填，如果必填，则生成内容为空的用例"""
        self.write_new_case_data(
            key=key,
            value='',
            detail=f"测试{key}参数为必填项，测试不输入内容发送请求",
            assert_data=self._assert_data(jsonpath="$.responseBody.result.retMsg", types="contains", value='OPEN357')
        )

    def _process_all_params(self, data):
        for key, value in data.items():
            # 判断当数据类型为字典的时候，递归调用继续处理，知道获取到参数内容为止
            if isinstance(value, dict):
                self._process_all_params(value)
            elif isinstance(value, list):
                for i in value:
                    self._process_all_params(i)
            else:

                try:
                    # 获取数据库中的数据
                    _key = self.get_sql_params()[key]
                    _field_type = _key['field_type']
                    _field_enums = _key['field_enums']
                    _field_length = _key['field_length']
                    _is_necessary = _key['is_necessary']
                    _case_id = self.get_case_id() + str(self.num)
                    # 判断数据类型为 str
                    if _field_type == FiledType.String.value:
                        self.field_length_generation_case(
                            key=key,
                            field_length=_field_length,
                        )
                    # 判断数据类型为枚举时
                    elif _field_type == FiledType.enum.value:
                        # 判断枚举开关为开启状态，才会生成用例
                        if _filed_enum_switch:
                            enum_type = _field_enums.split(",")
                            for i in enum_type:
                                self.filed_type_enums(
                                    key=key,
                                    enums=i
                                )
                    # 判断数据类型为时间
                    elif _field_type == FiledType.Timestamp.value:
                        self.filed_type_timestamp(
                            key=key
                        )

                    # 判断数据类型为decimal，随机生成 1-100的浮点数，保留两位，随机生成数据可以自定义
                    elif _field_type == FiledType.decimal.value:
                        self.filed_type_decimal(
                            key=key
                        )

                    # 判断参数是否必填
                    if _is_necessary == 'Y':
                        # _request_body1 = _request_body
                        self.filed_is_necessary(
                            key=key
                        )
                except KeyError:
                    WARNING.logger.warning(f"数据库中未找到{key}参数，请确认参数名称，如有疑惑请联系管理员")
                    continue

    def case_data_handler(self):
        """
        处理用例中的请求数据
        @return:
        """
        _request_body = self.get_request_body()
        # 递归处理所有参数
        self._process_all_params(_request_body)


if __name__ == '__main__':
    GenerateCaseDate().case_data_handler()

