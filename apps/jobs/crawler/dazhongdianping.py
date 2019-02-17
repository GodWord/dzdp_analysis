# -*- coding:utf-8 -*-
import time
import json
import pymysql
import requests
import traceback
import re
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome


class DaZhongDianPing:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko'
                              ') Chrome/61.0.3163.100 Safari/537.36'
            }
        )
        self.session.verify = False
        self.max_comment_page = 8
        self.conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='123456',
            db='dazhongdianping',
            charset='utf8mb4'
        )
        self.cur = self.conn.cursor()
        self.keyword = "农家乐美食"
        self.get_cookies("https://account.dianping.com/login")

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

    def mysql_insert(self, table, data):
        data = list(map(lambda x: pymysql.escape_string(str(x)), data))
        datalength = len(data)
        sql1 = 'insert into %s VALUES(' % table
        sql2 = '"%s",' * datalength % tuple(data)
        sql = sql1 + sql2[:-1] + ')'
        self.cur.execute(sql)

    def regex_findall(self, text, pattern):
        cr = re.compile(pattern, re.S)
        return cr.findall(text)

    def get_shop_list(self, page):
        url = 'http://www.dianping.com/search/keyword/16/0_%s/p%d' % (self.keyword, page)
        page = self.session.get(url).content.decode()
        soup = BeautifulSoup(page, 'lxml')
        shop_list = soup.find('div', {'class': 'shop-list J_shop-list shop-all-list'}).ul.find_all('li')
        for shop in shop_list:
            name = shop.find('div', {'class': 'tit'}).h4.text
            comment_num = shop.find('a', {'class': 'review-num'}).b.text
            try:
                avg_price = shop.find('a', {'class': 'mean-price'}).b.text
            except:
                avg_price = '0'
            rank = shop.find('div', {'class': 'comment'}).span.get('title')
            addr = shop.find('span', {'class': 'addr'}).text
            url = shop.a.get('href')
            shop_id = url.split('/')[-1]
            self.mysql_insert(table='shop', data=[shop_id, name, addr, avg_price, comment_num, rank])
            print(name)
            for i in range(self.max_comment_page):
                self.get_comment(shop_id, i)
                time.sleep(2)
            print(name, addr, rank, avg_price, comment_num, url, shop_id)
            self.conn.commit()

    def get_comment(self, shop_id, page):
        try:
            if page == 1:
                return
            url = 'http://www.dianping.com/shop/%s/review_all/p%d' % (shop_id, page)
            print(url)
            content = self.session.get(url).content.decode()
            soup = BeautifulSoup(content, 'html5lib')
            # print(soup.prettify())
            comment_list = soup.find('div', {'class': 'reviews-items'}).find_all('li', {'class': False})
            for comment in comment_list:
                name = comment.find('a', {'class': 'name'}).text.strip().replace('\r\n', '')
                vip = '是' if comment.find('span', {'class': 'vip'}) else '否'
                rank = self.regex_findall(str(comment), 'sml-str(.*?) star')[0]
                try:
                    content = comment.find('div', {'class': 'review-words Hide'}).text.strip()
                except:
                    try:
                        content = comment.find('div', {'class': 'review-truncated-words'}).text.strip()
                    except:
                        content = ' '
                comment_time = comment.find('span', {'class': 'time'}).text.strip()
                recommend = ','.join(list(map(lambda x: x.text, list(comment.find_all('a', {'class': 'col-exp'})))))
                score = ','.join(list(map(lambda x: x.text.strip(), list(comment.find_all('span', 'item')))))
                self.mysql_insert(table='comment',
                                  data=[shop_id, name, vip, rank, content, comment_time, recommend, score])
                self.conn.commit()
        except:
            return 0

    def run(self):
        for i in range(50):
            self.get_shop_list(i)
            time.sleep(2)


DaZhongDianPing().run()
