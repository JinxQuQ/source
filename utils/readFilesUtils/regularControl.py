"""
Desc : 自定义函数调用
# @Time : 2022/4/2 9:32 上午
# @Author : liuYunWin
"""
import json
import re
import datetime
from utils.otherUtils.jsonpath import jsonpath
from faker import Faker
import random
from utils.logUtils.logControl import ERROR
from utils.cacheUtils.cacheControl import Cache


class Context:
    def __init__(self):
        self.f = Faker(locale='zh_CN')

    def get_phone(self) -> int:
        """
        :return: 随机生成手机号码
        """
        phone = self.f.phone_number()
        return phone

    def get_job(self) -> str:
        """
        :return: 随机生成职业
        """

        job = self.f.job()
        return job

    def get_id_number(self) -> int:
        """

        :return: 随机生成身份证号码
        """

        id_number = self.f.ssn()
        return id_number

    def get_female_name(self) -> str:
        """

        :return: 女生姓名
        """
        female_name = self.f.name_female()
        return female_name

    def get_male_name(self) -> str:
        """

        :return: 男生姓名
        """
        male_name = self.f.name_male()
        return male_name

    def get_email(self) -> str:
        """

        :return: 生成邮箱
        """
        email = self.f.email()
        return email

    @classmethod
    def get_time(cls) -> str:
        """
        计算当前时间
        :return:
        """
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return now_time

    def random_int(self):
        """随机生成 0 - 9999 的数字"""
        numbers = self.f.random_int()
        return numbers

    @classmethod
    def host(cls) -> str:
        from utils.readFilesUtils.yamlControl import GetYamlData
        from common.setting import ConfigHandler

        # 从配置文件conf.yaml 文件中获取到域名，然后使用正则替换
        host = GetYamlData(ConfigHandler.config_path) \
            .get_yaml_data()['host']
        return host

    @classmethod
    def app_host(cls) -> str:
        """获取app的host"""
        from utils.readFilesUtils.yamlControl import GetYamlData
        from common.setting import ConfigHandler

        # 从配置文件conf.yaml 文件中获取到域名，然后使用正则替换
        host = GetYamlData(ConfigHandler.config_path) \
            .get_yaml_data()['app_host']
        return host


def sql_json(js_path, res):
    _sql_data = jsonpath(res, js_path)[0]
    if _sql_data is not False:
        return jsonpath(res, js_path)[0]
    else:
        raise ValueError(
            "sql 中的jsonpath数据未提取到，请检查语句是否正确",
            f"接口响应内容: {res}",
            f"jsonpath 提取规则: {js_path}"
        )


def regular(target):
    """
    新版本
    使用正则替换请求数据
    :return:
    """
    try:
        regular_pattern = r'\${{(.*?)}}'
        while re.findall(regular_pattern, target):
            key = re.search(regular_pattern, target).group(1)
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in key for i in value_types) is True:
                func_name = key.split(":")[1].split("(")[0]
                value_name = key.split(":")[1].split("(")[1][:-1]
                value_data = getattr(Context(), func_name)(*value_name.split(","))
                regular_int_pattern = r'\'\${{(.*?)}}\''
                target = re.sub(regular_int_pattern, str(value_data), target, 1)
            else:
                func_name = key.split("(")[0]
                value_name = key.split("(")[1][:-1]
                if value_name == "":
                    value_data = getattr(Context(), func_name)()
                else:
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                target = re.sub(regular_pattern, str(value_data), target, 1)
        return target

    except AttributeError:
        ERROR.logger.error("未找到对应的替换的数据, 请检查数据是否正确", target)
        raise


def sql_regular(value, res=None):
    """
    这里处理sql中的依赖数据，通过获取接口响应的jsonpath的值进行替换
    :param res: jsonpath使用的返回结果
    :param value:
    :return:
    """
    sql_json_list = re.findall(r"\$json\((.*?)\)\$", value)

    for i in sql_json_list:
        pattern = re.compile(r'\$json\(' + i.replace('$', "\$").replace('[', '\[') + r'\)\$')
        key = str(sql_json(i, res))
        value = re.sub(pattern, key, value, count=1)

    return value


def cache_regular(value):
    """
    通过正则的方式，读取缓存中的内容
    例：$cache{login_init}
    :param value:
    :return:
    """
    # 正则获取 $cache{login_init}中的值 --> login_init
    regular_dates = re.findall(r"\$cache\{(.*?)\}", value)

    # 拿到的是一个list，循环数据
    for regular_data in regular_dates:
        value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
        if any(i in regular_data for i in value_types) is True:
            value_types = regular_data.split(":")[0]
            regular_data = regular_data.split(":")[1]
            pattern = re.compile(r'\'\$cache{' + value_types.split(":")[0] + r'(.*?)}\'')
        else:
            pattern = re.compile(r'\$cache\{' + regular_data.replace('$', "\$").replace('[', '\[') + r'\}')
        cache_data = Cache(regular_data).get_cache()
        # 使用sub方法，替换已经拿到的内容
        value = re.sub(pattern, cache_data, value)
    return value


if __name__ == '__main__':
    a = regular("${{random_int(1,10)}}")
    print(a)
