#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/8/11 10:51
# @Author : 余少琪
"""
import json
from common.setting import ConfigHandler


# TODO swagger 导入
class SwaggerForYaml:
    def __init__(self):
        self._data = self.get_swagger_json()

    @classmethod
    def get_swagger_json(cls):
        """
        获取 swagger 中的 json 数据
        :return:
        """
        with open(
                ConfigHandler.common_path + "swagger-json.json", "r",
                encoding='utf-8'
        ) as f:
            row_data = json.load(f)
            return row_data

    def get_base_path(self):
        _base_path = self._data['basePath']

    def get_api_data(self):
        yaml_data = {
            "common": {
                "allureEpic": None,
                "allureFeature": None,
                "allureStory": None
            },
            "": {

            }
        }
        _api_data = self._data['paths']
        for k, v in _api_data.items():
            print(k, v)


if __name__ == '__main__':
    SwaggerForYaml().get_api_data()
