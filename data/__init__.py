#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 10:49
# @Author : 余少琪


def urls(path, url):
    host = None
    for i in url:

        if 'yushaoqi' in path:
            host = '${{host}}'
        else:
            host = path.split(i)
    return host


if __name__ == '__main__':
   a=  urls(path='http://parkyz.kkx88.cn/api/biz/drainPipeNetworkArchives/list?pageNum=1&pageSize=10', url = ["https://www.wanandroid.com", "http://parkyz.kkx88.cn/"])
   print(a)
   url = 'http://parkyz.kkx88.cn/api/biz/drainPipeNetworkArchives/list?pageNum=1&pageSize=10'
   print(url.split('http://parkyz.kkx88.cn')[-1])