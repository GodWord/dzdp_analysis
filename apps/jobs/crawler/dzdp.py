# -*- coding:utf-8 -*-
__author__ = 'zhoujifeng'
__date__ = '2019/2/17 22:10'

from selenium.webdriver import Chrome

class DZDP:
    def __init__(self):
        pass

    def get_cookies(self, url):
        driver = Chrome()
        driver.get(url)
        # 打开selenium，跳转到登录页面
        input('Enter any key to continue...')
        # 等待用户手动登录完成
        cookies = dict()
        for item in driver.get_cookies():
            cookies[item["name"]] = item["value"]
        # 获取selenium里的cookies 保存成dict格式
        self.session.cookies.update(cookies)
        # 将cookies加载到session对象中
