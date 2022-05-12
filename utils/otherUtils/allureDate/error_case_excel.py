#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/5/8 21:37
# @Author  : 余少琪
# @Email   : 1603453211@qq.com
# @File    : error_case_excel
# @describe:

import xlwings
import json
import shutil
import os
from utils.readFilesUtils.get_all_files_path import get_all_files
from common.setting import ConfigHandler
from utils.noticUtils.weChatSendControl import WeChatSend


# TODO 还需要处理动态值
class ErrorTestCase:
    """ 收集错误的excel """
    def __init__(self):
        self.test_case_path = ConfigHandler.report_html_test_case_path

    def get_error_case_data(self):
        """
        收集所有失败用例的数据
        @return:
        """
        path = get_all_files(self.test_case_path)
        files = []
        for i in path:
            with open(i, 'r', encoding='utf-8') as fp:
                date = json.load(fp)
                if date['status'] == 'failed' or date['status'] == 'broken':
                    files.append(date)
        return files

    @classmethod
    def get_case_name(cls, test_case):
        """
        收集测试用例名称
        @return:
        """
        name = test_case['name'].split('[')
        case_name = name[1][:-1]
        return case_name

    @classmethod
    def get_parameters(cls, test_case):
        """
        获取allure报告中的 parameters 参数内容
        @return:
        """
        parameters = test_case['parameters'][0]['value']
        return eval(parameters)

    def get_case_url(self, test_case):
        """
        获取测试用例的 url
        @param test_case:
        @return:
        """
        url = self.get_parameters(test_case)['url']
        return url

    def get_method(self, test_case):
        """
        获取用例中的请求方式
        @param test_case:
        @return:
        """
        method = self.get_parameters(test_case)['method']
        return method

    def get_headers(self, test_case):
        """
        获取用例中的请求头
        @return:
        """
        headers = self.get_parameters(test_case)['headers']
        return headers

    def get_request_type(self, test_case):
        """
        获取用例的请求类型
        @param test_case:
        @return:
        """
        request_type = self.get_parameters(test_case)['requestType']
        return request_type

    def get_case_data(self, test_case):
        """
        获取用例内容
        @return:
        """
        case_data = self.get_parameters(test_case)['data']
        return case_data

    def get_dependence_case(self, test_case):
        """
        获取依赖用例
        @param test_case:
        @return:
        """
        dependence_case_data = self.get_parameters(test_case)['dependence_case_data']
        return dependence_case_data

    def get_sql(self, test_case):
        """
        获取 sql 数据
        @param test_case:
        @return:
        """
        sql = self.get_parameters(test_case)['sql']
        return sql

    def get_assert(self, test_case):
        """
        获取断言数据
        @param test_case:
        @return:
        """
        assert_data = self.get_parameters(test_case)['assert']
        return assert_data

    @classmethod
    def get_response(cls, test_case):
        """
        获取响应内容的数据
        @param test_case:
        @return:
        """
        try:
            res_data_attachments = test_case['testStage']['steps'][7]['attachments'][0]['source']
            path = ConfigHandler.report_html_attachments_path + res_data_attachments
            with open(path, 'r', encoding='utf-8') as fp:
                date = json.load(fp)
            return date
        except FileNotFoundError:
            return "程序中未检测到响应内容附件信息"

    @classmethod
    def get_case_time(cls, test_case):
        """
        获取用例运行时长
        @param test_case:
        @return:
        """
        case_time = str(test_case['time']['duration']) + "ms"
        return case_time

    @classmethod
    def get_uid(cls, test_case):
        """
        获取 allure 报告中的 uid
        @param test_case:
        @return:
        """
        uid = test_case['uid']
        return uid


class ErrorCaseExcel:
    """ 收集运行失败的用例，整理成excel报告 """
    def __init__(self):
        _excel_template = ConfigHandler.excel_template + "自动化异常测试用例.xlsx"
        self._file_path = ConfigHandler.file_path + "自动化异常测试用例.xlsx"
        if os.path.exists(self._file_path):
            os.remove(self._file_path)

        shutil.copyfile(src=_excel_template, dst=self._file_path)

        # 打开程序（只打开不新建
        self.app = xlwings.App(visible=False, add_book=False)
        self.wb = self.app.books.open(self._file_path)

        # 选取工作表：
        self.sheet = self.wb.sheets['异常用例']  # 或通过索引选取
        self.case_data = ErrorTestCase()

    def background_color(self, position: str, rgb: tuple):
        """
        excel 单元格设置背景色
        @param rgb: rgb 颜色 rgb=(0，255，0)
        @param position: 位置，如 A1, B1...
        @return:
        """
        # 定位到单元格位置
        rng = self.sheet.range(position)
        excel_rgb = rng.color = rgb
        return excel_rgb

    def column_width(self, position: str, width: int):
        """
        设置列宽
        @return:
        """
        rng = self.sheet.range(position)
        # 列宽
        excel_column_width = rng.column_width = width
        return excel_column_width

    def row_height(self, position, height):
        """
        设置行高
        @param position:
        @param height:
        @return:
        """
        rng = self.sheet.range(position)
        excel_row_height = rng.row_height = height
        return excel_row_height

    def column_width_adaptation(self, position):
        """
        excel 所有列宽度自适应
        @return:
        """
        rng = self.sheet.range(position)
        auto_fit = rng.columns.autofit()
        return auto_fit

    def row_width_adaptation(self, position):
        """
        excel 设置所有行宽自适应
        @return:
        """
        rng = self.sheet.range(position)
        row_adaptation = rng.rows.autofit()
        return row_adaptation

    def write_excel_content(self, position: str, value: str):
        """
        excel 中写入内容
        @param value:
        @param position:
        @return:
        """
        self.sheet.range(position).value = value

    def write_case(self):
        """
        用例中写入失败用例数据
        @return:
        """

        dates = self.case_data.get_error_case_data()
        # 判断有数据才进行写入
        if len(dates) > 0:
            num = 2
            for date in dates:
                print(self.case_data.get_headers(date))
                self.write_excel_content(position="A" + str(num), value=str(self.case_data.get_uid(date)))
                self.write_excel_content(position='B' + str(num), value=str(self.case_data.get_case_name(date)))
                self.write_excel_content(position="C" + str(num), value=str(self.case_data.get_case_url(date)))
                self.write_excel_content(position="D" + str(num), value=str(self.case_data.get_method(date)))
                self.write_excel_content(position="E" + str(num), value=str(self.case_data.get_request_type(date)))
                self.write_excel_content(position="F" + str(num), value=str(self.case_data.get_headers(date)))
                self.write_excel_content(position="G" + str(num), value=str(self.case_data.get_case_data(date)))
                self.write_excel_content(position="H" + str(num), value=str(self.case_data.get_dependence_case(date)))
                self.write_excel_content(position="I" + str(num), value=str(self.case_data.get_assert(date)))
                self.write_excel_content(position="J" + str(num), value=str(self.case_data.get_sql(date)))
                self.write_excel_content(position="K" + str(num), value=str(self.case_data.get_case_time(date)))
                self.write_excel_content(position="L" + str(num), value=str(self.case_data.get_response(date)))
                num += 1
            self.wb.save()
            self.wb.close()
            self.app.quit()
            # 有数据才发送企业微信
            WeChatSend().send_file_msg(self._file_path)


if __name__ == '__main__':
    ErrorCaseExcel().write_case()