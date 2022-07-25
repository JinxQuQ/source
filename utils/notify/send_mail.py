#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/29 14:57
# @Author : 余少琪
描述: 发送邮件
"""

import smtplib
from email.mime.text import MIMEText
from common.setting import ConfigHandler
from utils.read_files_tools.yaml_control import GetYamlData
from utils.other_tools.allure_data.allure_report_data import TestMetrics, AllureFileClean


class SendEmail:
    """ 发送邮箱 """
    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.get_data = GetYamlData(ConfigHandler.config_path).get_yaml_data()['email']
        self.send_user = self.get_data['send_user']  # 发件人
        self.email_host = self.get_data['email_host']  # QQ 邮件 STAMP 服务器地址
        self.key = self.get_data['stamp_key']  # STAMP 授权码
        self.name = GetYamlData(ConfigHandler.config_path).get_yaml_data()['ProjectName'][0]

    def send_mail(self, user_list: list, sub, content: str) -> None:
        """

        @param user_list: 发件人邮箱
        @param sub:
        @param content: 发送内容
        @return:
        """
        user = "余少琪" + "<" + self.send_user + ">"
        message = MIMEText(content, _subtype='plain', _charset='utf-8')
        message['Subject'] = sub
        message['From'] = user
        message['To'] = ";".join(user_list)
        server = smtplib.SMTP()
        server.connect(self.email_host)
        server.login(self.send_user, self.key)
        server.sendmail(user, user_list, message.as_string())
        server.close()

    def error_mail(self, error_message: str) -> None:
        """
        执行异常邮件通知
        @param error_message: 报错信息
        @return:
        """
        email = self.get_data['send_list']
        user_list = email.split(',')  # 多个邮箱发送，config文件中直接添加  '806029174@qq.com'

        sub = self.name + "接口自动化执行异常通知"
        content = f"自动化测试执行完毕，程序中发现异常，请悉知。报错信息如下：\n{error_message}"
        self.send_mail(user_list, sub, content)

    def send_main(self) -> None:
        """
        发送邮件
        :return:
        """
        email = self.get_data["send_list"]
        user_list = email.split(',')  # 多个邮箱发送，yaml文件中直接添加  '806029174@qq.com'

        sub = self.name + "接口自动化报告"
        content = f"""
        各位同事, 大家好:
            自动化用例执行完成，执行结果如下:
            用例运行总数: {self.metrics.total} 个
            通过用例个数: {self.metrics.passed} 个
            失败用例个数: {self.metrics.failed} 个
            异常用例个数: {self.metrics.broken} 个
            跳过用例个数: {self.metrics.skipped} 个
            成  功   率: {self.metrics.pass_rate} %


        **********************************
        jenkins地址：https://121.xx.xx.47:8989/login
        详细情况可登录jenkins平台查看，非相关负责人员可忽略此消息。谢谢。
        """
        self.send_mail(user_list, sub, content)


if __name__ == '__main__':
    SendEmail(AllureFileClean().get_case_count()).send_main()
