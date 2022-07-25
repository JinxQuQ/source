"""
# @Time   : 2022/3/28 10:52
# @Author : 余少琪
"""
import types
from typing import Dict, Text, Callable


def load_module_functions(module) -> Dict[Text, Callable]:
    """ 获取 module中方法的名称和所在的内存地址 """
    module_functions = {}

    for name, item in vars(module).items():
        if isinstance(item, types.FunctionType):
            module_functions[name] = item
    return module_functions
