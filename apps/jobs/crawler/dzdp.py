# -*- coding:utf-8 -*-
import json
import os
import re

import requests

from setting.setting import HEADERS, BASE_DIR, LOGIN_URL, PROXIES_API_URL
from utils import CrawlerUtils

__author__ = 'zhoujifeng'
__date__ = '2019/2/17 22:10'

from selenium.webdriver import Chrome


class DZDP:
    def __init__(self, keyword):
        self.session = requests.Session()
        self.session.headers.update(CrawlerUtils.get_headers(HEADERS))
        self.get_cookies(LOGIN_URL)
        self.keyword = keyword
        self.session.proxies = CrawlerUtils.get_proxies(PROXIES_API_URL)

    def get_cookies(self, url):
        driver = Chrome()
        # 打开selenium，跳转到登录页面
        driver.get(url)
        # 等待用户手动登录完成
        input('Enter any key to continue...')
        # 获取selenium里的cookies 保存成dict格式
        cookies = dict()
        for item in driver.get_cookies():
            cookies[item["name"]] = item["value"]

        # 将cookies加载到session对象中
        self.session.cookies.update(cookies)
        with open(os.path.join(BASE_DIR, 'setting/cookies.json'), 'w', encoding='utf-8')as f:
            json.dump(cookies, f, ensure_ascii=False)
            f.write('\n')

    def get_shop_list(self, page):
        url = 'http://www.dianping.com/search/keyword/1/10_%s/p%d' % (self.keyword, page)
        html = self.session.get(url).content.decode()
        css_url_regex = re.compile(r'href="//(s3plus.meituan.net.*?)\"')
        css_url = re.search(css_url_regex, html).group(1)
        css_url = 'http://' + css_url
        # 获取css文件
        css_resp = requests.get(css_url)
        regex_kj_svg = re.compile(r'span\[class\^="kj-"\][\s\S]*?url\((.*?)\)')
        css_html = css_resp.content.decode('utf-8')
        # 从css文件中匹配出svg文件的url
        svg_kj_url = re.search(regex_kj_svg, css_html).group(1)
        svg_kj_url = 'http:' + svg_kj_url
        svg_kj_resp = requests.get(svg_kj_url)
        svg_kj_html = svg_kj_resp.text
        # 匹配出svg图片的10个数字
        number = re.search(r'\d{10}', svg_kj_html).group()
        # 匹配出以kj-开头的class属性
        regex_kjs_css = re.compile(r'\.(kj-\w{4})[\s\S]*?-(\d+)')
        kjs = re.findall(regex_kjs_css, css_html)
        kjs = {i[0]: int(i[1]) for i in kjs}
        # 根据偏移量排序
        temp = sorted(kjs.items(), key=lambda x: x[1])
        # 将class属性与其表示的数字组成字典
        kjs = {temp[i][0]: number[i] for i in range(10)}

        # soup = BeautifulSoup(page, 'lxml')
        # shop_list = soup.find('div', {'class': 'shop-list J_shop-list shop-all-list'}).ul.find_all('li')
        # for shop in shop_list:
        #     name = shop.find('div', {'class': 'tit'}).h4.text
        #     comment_num = shop.find('a', {'class': 'review-num'}).b.text
        #     try:
        #         avg_price = shop.find('a', {'class': 'mean-price'}).b.text
        #     except:
        #         avg_price = '0'
        #     rank = shop.find('div', {'class': 'comment'}).span.get('title')
        #     addr = shop.find('span', {'class': 'addr'}).text
        #     url = shop.a.get('href')
        #     shop_id = url.split('/')[-1]
        #     self.mysql_insert(table='shop', data=[shop_id, name, addr, avg_price, comment_num, rank])
        #     print(name)
        #     for i in range(self.max_comment_page):
        #         self.get_comment(shop_id, i)
        #         time.sleep(2)
        #     print(name, addr, rank, avg_price, comment_num, url, shop_id)
        #     self.conn.commit()

    def run(self):
        self.get_shop_list(1)
