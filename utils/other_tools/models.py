import json
import types
from enum import Enum, unique
from typing import Text, Dict, Callable, Union, Optional, List, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field


class NotificationType(Enum):
    """ 自动化通知方式 """
    DEFAULT = 0
    DING_TALK = 1
    WECHAT = 2
    EMAIL = 3
    FEI_SHU = 4


@dataclass
class TestMetrics:
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: Text


class RequestType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    JSON = "JSON"
    PARAMS = "PARAMS"
    DATA = "DATA"
    FILE = 'FILE'
    EXPORT = "EXPORT"
    NONE = "NONE"


def load_module_functions(module) -> Dict[Text, Callable]:
    """ 获取 module中方法的名称和所在的内存地址 """
    module_functions = {}

    for name, item in vars(module).items():
        if isinstance(item, types.FunctionType):
            module_functions[name] = item
    return module_functions


@unique
class DependentType(Enum):
    """
    数据依赖相关枚举
    """
    RESPONSE = 'response'
    REQUEST = 'request'
    SQL_DATA = 'sqlData'
    CACHE = "cache"


class Assert(BaseModel):
    jsonpath: Text
    type: Text
    value: Any
    AssertType: Union[None, Text] = None


class DependentData(BaseModel):
    dependent_type: Text
    jsonpath: Text
    set_cache: Optional[Text]
    replace_key: Optional[Text]


class DependentCaseData(BaseModel):
    case_id: Text
    dependent_data: List[DependentData]


class ParamPrepare(BaseModel):
    dependent_type: Text
    jsonpath: Text
    set_cache: Text


class SendRequest(BaseModel):
    dependent_type: Text
    jsonpath: Optional[Text]
    cache_data: Optional[Text]
    set_cache: Optional[Text]
    replace_key: Optional[Text]


class TearDown(BaseModel):
    case_id: Text
    param_prepare: Optional[List["ParamPrepare"]]
    send_request: Optional[List["SendRequest"]]


class CurrentRequestSetCache(BaseModel):
    type: Text
    jsonpath: Text
    name: Text


class TestCase(BaseModel):
    url: Text
    method: Text
    detail: Text
    assert_data: Union[Dict, Text] = Field([], alias="assert")
    headers: Union[None, Dict, Text] = {}
    requestType: Text
    is_run: Union[None, bool] = None
    data: Union[Dict, None, Text] = None
    dependence_case: Union[None, bool] = False
    dependence_case_data: Optional[Union[None, List["DependentCaseData"], Text]] = None
    sql: List = None
    setup_sql: List = None
    status_code: Optional[int] = None
    teardown_sql: Optional[List] = None
    teardown: List["TearDown"] = None
    current_request_set_cache: Optional[List["CurrentRequestSetCache"]]
    sleep: Optional[Union[int, float]]


class ResponseData(BaseModel):
    url: Text
    is_run: Union[None, bool]
    detail: Text
    response_data: Text
    request_body: Union[Dict, None]
    method: Text
    sql_data: Dict
    yaml_data: "TestCase"
    headers: Dict
    cookie: Dict
    assert_data: List = Field([], alias="assert")
    res_time: Union[int, float]
    status_code: int
    teardown: List["TearDown"] = None
    teardown_sql: Union[None, List]
    body: Union[Dict, None] = None


@unique
class AllureAttachmentType(Enum):
    """
    allure 报告的文件类型枚举
    """
    TEXT = "txt"
    CSV = "csv"
    TSV = "tsv"
    URI_LIST = "uri"

    HTML = "html"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"
    PCAP = "pcap"

    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"

    MP4 = "mp4"
    OGG = "ogg"
    WEBM = "webm"

    PDF = "pdf"


@unique
class AssertMethod(Enum):
    """断言类型"""
    # 是否相等
    equals = "=="
    # 判断实际结果小于预期结果
    less_than = "lt"
    # 判断实际结果小于等于预期结果
    less_than_or_equals = "le"
    # 判断实际结果大于预期结果
    greater_than = "gt"
    # 判断实际结果大于等于预期结果
    greater_than_or_equals = "ge"
    # 判断实际结果不等于预期结果
    not_equals = "not_eq"
    # 判断字符串是否相等
    string_equals = "str_eq"
    # 判断长度是否相等
    length_equals = "len_eq"
    # 判断长度大于
    length_greater_than = "len_gt"
    # 判断长度大于等于
    length_greater_than_or_equals = 'len_ge'
    # 判断长度小于
    length_less_than = "len_lt"
    # 判断长度小于等于
    length_less_than_or_equals = 'len_le'
    # 判断期望结果内容包含在实际结果中
    contains = "contains"
    # 判断实际结果包含在期望结果中
    contained_by = 'contained_by'
    # 检查响应内容的开头是否和预期结果内容的开头相等
    startswith = 'startswith'
    # 检查响应内容的结尾是否和预期结果内容相等
    endswith = 'endswith'
