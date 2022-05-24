#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/5/23 21:27
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : encryption_algorithm_control
# @describe:

import hashlib
from hashlib import sha256
import hmac
from pyDes import *
import binascii


def hmac_sha256_encrypt(key, data):
    """hmac sha 256算法"""
    _key = key.encode('utf8')
    _data = data.encode('utf8')
    encrypt_data = hmac.new(_key, _data, digestmod=sha256).hexdigest()
    return encrypt_data


def md5_encryption(value):
    """ md5 加密"""
    str_md5 = hashlib.md5(str(value).encode(encoding='utf-8')).hexdigest()
    return str_md5


def sha1_secret_str(s: str):
    """
    使用sha1加密算法，返回str加密后的字符串
    """
    encrypts = hashlib.sha1(s.encode('utf-8')).hexdigest()
    return encrypts


def des_encrypt(s):
    """
    DES 加密
    :param s: 原始字符串
    :return: 加密后字符串，16进制
    """
    # 密钥，自行修改
    _KEY = 'PASSWORD'
    secret_key = _KEY
    iv = secret_key
    k = des(secret_key, ECB, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return binascii.b2a_hex(en)


def encryption(ency_type):
    """
    :param ency_type: 加密类型
    :return:
    """
    def decorator(func):
        def swapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if kwargs != {}:
                params = kwargs['yaml_data']['data']
            else:
                params = args[1]['data']
            if ency_type == "md5":
                def ency_value(data):
                    for k, v in data.items():
                        if isinstance(v, dict):
                            ency_value(data=v)
                        else:
                            print(k, v)
                            data[k] = md5_encryption(v)
                    return data

            else:
                raise ValueError("暂不支持该加密规则，如有需要，请联系管理员")
            ency_value(params)
            return res

        return swapper

    return decorator


if __name__ == '__main__':
    def getvalue(data: dict):
        for k, v in data.items():
            if isinstance(v, dict):
                getvalue(v)
            else:
                v = str(v) + "i"
                data[k] = v
        return data
    a = getvalue({'id': '20175', 'tester': {'yushaoqi': 123, 'woshi': {'liuming': 345}}})
    print(a)