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

    @property
    def test_random(self) -> int:
        """
        :return: 随机数
        """
        rn = random.randint(0, 5000)
        return rn

    @property
    def get_video_plan_name(self) -> str:
        """
        :return: 随机计划名
        """
        name = "ci短视频计划" + str(random.randint(0, 5000))
        return name

    @property
    def get_live_plan_name(self) -> str:
        """
        :return: 随机计划名
        """
        name = "ci直播计划" + str(random.randint(0, 5000))
        return name

    @property
    def get_group_live_name(self) -> str:
        """
        :return: 随机计划组名
        """
        name = "ci直播组" + str(random.randint(0, 5000))
        return name

    @property
    def get_group_video_name(self) -> str:
        """
        :return: 随机计划组名
        """
        name = "ci短视频组" + str(random.randint(0, 5000))
        return name

    @property
    def get_phone(self) -> int:
        """
        :return: 随机生成手机号码
        """
        phone = self.f.phone_number()
        return phone

    @property
    def get_job(self) -> str:
        """

        :return: 随机生成身份证号码
        """

        job = self.f.job()
        return job

    @property
    def get_id_number(self) -> int:
        """

        :return: 随机生成身份证号码
        """

        id_number = self.f.ssn()
        return id_number

    @property
    def get_female_name(self) -> str:
        """

        :return: 女生姓名
        """
        female_name = self.f.name_male()
        return female_name

    @property
    def get_male_name(self) -> str:
        """

        :return: 男生姓名
        """
        male_name = self.f.name_female()
        return male_name

    @property
    def get_email(self) -> str:
        """

        :return: 生成邮箱
        """
        email = self.f.email()
        return email

    @property
    def get_time(self) -> str:
        """
        计算当前时间
        :return:
        """
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return nowtime

    @property
    def random_int(self):
        """随机生成 0 - 9999 的数字"""
        numbers = self.f.random_int()
        return numbers

    @property
    def host(self) -> str:
        from utils.readFilesUtils.yamlControl import GetYamlData
        from common.setting import ConfigHandler

        # 从配置文件conf.yaml 文件中获取到域名，然后使用正则替换
        host = GetYamlData(ConfigHandler.config_path) \
            .get_yaml_data()['host']
        return host

    @property
    def app_host(self) -> str:
        """获取app的host"""
        from utils.readFilesUtils.yamlControl import GetYamlData
        from common.setting import ConfigHandler

        # 从配置文件conf.yaml 文件中获取到域名，然后使用正则替换
        host = GetYamlData(ConfigHandler.config_path) \
            .get_yaml_data()['app_host']
        return host


def sql_json(js_path, res):
    return jsonpath(res, js_path)[0]


def regular(target):
    """
    使用正则替换请求数据
    :return:
    """
    try:
        regular_pattern = r'\${{(.*?)}}'
        while re.findall(regular_pattern, target):
            key = re.search(regular_pattern, target).group(1)
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in key for i in value_types) is True:
                value_data = getattr(Context(), key.split(":")[1])
                regular_int_pattern = r'\'\${{(.*?)}}\''
                target = re.sub(regular_int_pattern, str(value_data), target, 1)
            else:
                value_data = getattr(Context(), key)
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


def replace_load(value):
    """
    使用热加载的方式替换解析yaml中的数据
    调用这个方法，可以支持yaml中函数方法可以传参，但是目前返回的类型必须都是str类型的
    """
    if value and isinstance(value, dict):
        str_data = json.dumps(value)
    else:
        str_data = value
    for i in range(1, str_data.count('${{') + 1):
        if "${{" in str_data and "}}" in str_data:
            start_index = str_data.index("${{")
            end_index = str_data.index("}}", start_index)
            old_value = str_data[start_index:end_index + 2]
            func_name = old_value[3:old_value.index("(")]
            args_value = old_value[old_value.index("(") + 1:old_value.index(")")]
            # 反射
            new_value = getattr(Context(), func_name)(*args_value.split(","))
            str_data = str_data.replace(old_value, str(new_value))
        else:
            if value and isinstance(value, dict):
                value = json.loads(str_data)
            else:
                value = str_data
    return str_data
