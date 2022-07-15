#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 14:18
# @Author : 余少琪
import json
import types
from typing import Text, Dict, Callable, Any, Union
from utils.otherUtils.jsonpath import jsonpath
from utils.otherUtils.get_conf_data import sql_switch
from utils.logUtils.logControl import ERROR, WARNING
from Enums.assertMethod_enum import AssertMethod
from utils.assertUtils import assert_type
from utils.readFilesUtils.regularControl import cache_regular


class Assert:

    def __init__(self, assert_data: Dict):
        self.assert_data = eval(cache_regular(str(assert_data)))
        self.functions_mapping = self.load_module_functions(assert_type)

    @staticmethod
    def _check_params(
            response_data: Text, sql_data: Union[Dict, None]) -> bool:
        """

        :param response_data: 响应数据
        :param sql_data: 数据库数据
        :return:
        """
        # 用例如果不执行，接口返回的相应数据和数据库断言都是 False，这里则判断跳过断言判断
        if (response_data and sql_data) is False:
            return False
        else:
            # 判断断言的数据类型
            if isinstance(sql_data, dict):
                ...
            else:
                raise ValueError(
                    "断言失败，response_data、sql_data的数据类型必须要是字典类型，"
                    "请检查接口对应的数据是否正确\n"
                    f"sql_data: {sql_data}, 数据类型: {type(sql_data)}\n"
                )

    @classmethod
    def load_module_functions(cls, module) -> Dict[Text, Callable]:
        """ 获取 module中方法的名称和所在的内存地址 """
        module_functions = {}

        for name, item in vars(module).items():
            if isinstance(item, types.FunctionType):
                module_functions[name] = item
        return module_functions

    @classmethod
    def res_sql_data_bytes(cls, res_sql_data: Any) -> Text:
        """ 处理 mysql查询出来的数据类型如果是bytes类型，转换成str类型 """
        if isinstance(res_sql_data, bytes):
            res_sql_data = res_sql_data.decode('utf=8')
        return res_sql_data

    def sql_switch_handle(
            self,
            sql_data: Dict,
            assert_value: Any,
            key: Text,
            values: Any,
            resp_data: Dict) -> None:
        """

        :param sql_data: 测试用例中的sql
        :param assert_value: 断言内容
        :param key:
        :param values:
        :param resp_data: 预期结果
        :return:
        """
        # 判断数据库为开关为关闭状态
        if sql_switch() is False:
            WARNING.logger.warning(
                f"检测到数据库状态为关闭状态，程序已为您跳过此断言，断言值:{values}"
            )
        # 数据库开关为开启
        if sql_switch():
            # 判断当用例走的数据数据库断言，但是用例中未填写SQL
            if sql_data == {'sql': None}:
                raise ValueError("请在用例中添加您要查询的SQL语句。")
            # 走正常SQL断言逻辑
            else:
                res_sql_data = jsonpath(sql_data, assert_value)
                if res_sql_data is False:
                    raise ValueError(
                        f"数据库断言内容jsonpath提取失败， 当前jsonpath内容: {assert_value}\n"
                        f"数据库返回内容: {sql_data}"
                    )

                # 判断mysql查询出来的数据类型如果是bytes类型，转换成str类型
                res_sql_data = self.res_sql_data_bytes(res_sql_data[0])
                name = AssertMethod(self.assert_data[key]['type']).name
                self.functions_mapping[name](resp_data[0], res_sql_data)

    def assert_type_handle(
            self,
            assert_types: Union[Text, None],
            sql_data: Union[Dict, None],
            assert_value: Any,
            key: Text,
            values: Dict,
            resp_data: Any) -> None:

        # 判断断言类型
        if assert_types == 'SQL':
            self.sql_switch_handle(
                sql_data=sql_data,
                assert_value=assert_value,
                key=key,
                values=values,
                resp_data=resp_data)

        # 判断assertType为空的情况下，则走响应断言
        elif assert_types is None:
            name = AssertMethod(self.assert_data[key]['type']).name
            self.functions_mapping[name](resp_data[0], assert_value)
            print(resp_data[0], assert_value)
        else:
            raise ValueError("断言失败，目前只支持数据库断言和响应断言")

    def assert_equality(
            self,
            response_data: Text,
            sql_data: Dict,
            status_code: int) -> None:

        # 判断数据类型
        if self._check_params(response_data, sql_data) is not False:
            for key, values in self.assert_data.items():
                if key == "status_code":
                    assert status_code == values
                else:
                    assert_value = self.assert_data[key]['value']  # 获取 yaml 文件中的期望value值
                    assert_jsonpath = self.assert_data[key]['jsonpath']  # 获取到 yaml断言中的jsonpath的数据
                    assert_types = self.assert_data[key]['AssertType']
                    # 从yaml获取jsonpath，拿到对象的接口响应数据
                    resp_data = jsonpath(json.loads(response_data), assert_jsonpath)

                    # jsonpath 如果数据获取失败，会返回False，判断获取成功才会执行如下代码
                    if resp_data is not False:
                        # 判断断言类型
                        self.assert_type_handle(
                            assert_types=assert_types,
                            sql_data=sql_data,
                            assert_value=assert_value,
                            key=key,
                            values=values,
                            resp_data=resp_data)
                    else:
                        ERROR.logger.error("JsonPath值获取失败{}".format(assert_jsonpath))
                        raise ValueError(f"JsonPath值获取失败{assert_jsonpath}")


if __name__ == '__main__':
    pass
