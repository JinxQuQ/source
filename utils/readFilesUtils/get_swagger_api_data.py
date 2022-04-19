# coding=utf-8

import json
from common.setting import ConfigHandler


# TODO: 从swagger导出json文件，转成yaml格式的测试用例
class SwaggerApiJson:
    """获取swagger中的api数据，然后转换成yaml用例"""

    def __init__(self):
        self.file_path = ConfigHandler.file_path + '/2.系统模块_OpenAPI.json'
        self.case_id_num = 0

    def get_api_json(self):
        """拿到json文件中的数据"""

        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['paths']

    def get_case_id(self, url):
        """
        根据请求url, 生成 yaml 用例中的 case_id
        :param url: /system/user/authRole
        :return: authRole_1
        """
        case_name = url.split("/")[-1]
        case_id = case_name + "_" + str(self.case_id_num)
        self.case_id_num += 1
        return case_id

    @classmethod
    def get_url(cls, json_data):
        """
        获取请求 path
        :param json_data:
        :return:
        """
        return json_data

    def get_detail(self):
        pass

    @classmethod
    def get_request_body(cls, json_data):
        request_type = 'JSON'
        """获取请求参数内容"""
        if 'requestBody' in json_data:
            request_type = 'JSON'
            return json_data['requestBody'], request_type
        elif 'parameters' in json_data:
            request_type = 'PARAMS',  request_type
            return json_data['parameters'], request_type
        else:
            return None, request_type

    def get_headers(self, json_data):
        """获取请求头"""
        pass

    def get_host(self):
        """获取host"""
        yaml_data = {}
        api_json = self.get_api_json()
        for k, v in api_json.items():
            case_id = self.get_case_id(k)
            yaml_data[case_id] = {}
            yaml_data[case_id]['url'] = k
            for key, value in v.items():
                yaml_data[case_id]['method'] = key
                yaml_data[case_id]['detail'] = value['summary']
                yaml_data[case_id]['data'] = self.get_request_body(value)[0]
                yaml_data[case_id]['requestType'] = self.get_request_body([1])
                yaml_data[case_id]['headers'] = '1'
                # print(key, value)
        print(yaml_data)


if __name__ == '__main__':
    SwaggerApiJson().get_host()
    # SwaggerApiJson().get_request_body(
    #     {'request1ody': {'content': {'application/json': {'schema': {'$ref': '#/components/schemas/参数配置业务对象'}}}}})
    SwaggerApiJson().get_case_id('/system/user/authRole/{userId}')
