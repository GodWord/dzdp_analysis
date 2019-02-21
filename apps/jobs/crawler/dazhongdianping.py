# -*- coding:utf-8 -*-
import math
import re
import time

import lxml.html as H
import pymysql
import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome

from setting.setting import PROXIES_API_URL
from utils import CrawlerUtils


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
        self.session.proxies = CrawlerUtils.get_proxies(PROXIES_API_URL)

        self.conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='training',
            db='dzdp_db',
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

    def get_tag(self, _list, offset=1):
        _new_list = [data[0:offset] for data in _list]

        if len(set(_new_list)) == 1:
            # 说明全部重复
            offset += 1
            return self.get_tag(_list, offset)
        else:
            _return_data = [data[0:offset - 1] for data in _list][0]

            return _return_data

    def get_css(self, content):
        matched = re.search(r'href="([^"]+svgtextcss[^"]+)"', content, re.M)
        if not matched:
            raise Exception("cannot find svgtextcss file")
        css_url = matched.group(1)

        css_url = "https:" + css_url
        class_tag = re.findall("<b><span class=\"(.*?)\"></span>", content)
        _tag = self.get_tag(class_tag)

        return css_url, _tag

    def mysql_insert(self, table, data):
        print(data)
        data = list(map(lambda x: pymysql.escape_string(str(x)), data))
        datalength = len(data)
        sql1 = 'insert into %s VALUES(' % table
        sql2 = '"%s",' * datalength % tuple(data)
        sql = sql1 + sql2[:-1] + ')'
        self.cur.execute(sql)

    def regex_findall(self, text, pattern):
        cr = re.compile(pattern, re.S)
        return cr.findall(text)

    def get_css_and_px_dict(self, css_url):
        con = self.session.get(css_url).content.decode("utf-8")
        find_datas = re.findall(r'(\.[a-zA-Z0-9-]+)\{background:(\-\d+\.\d+)px (\-\d+\.\d+)px', con)
        css_name_and_px = {}
        for data in find_datas:
            # 属性对应的值
            span_class_attr_name = data[0][1:]
            # 偏移量
            offset = data[1]
            # 阈值
            position = data[2]
            css_name_and_px[span_class_attr_name] = [offset, position]
        return css_name_and_px

    def get_svg_threshold_and_int_dict(self, css_url, _tag):
        con = self.session.get(css_url).content.decode("utf-8")
        index_and_word_dict = {}
        # 根据tag值匹配到相应的svg的网址

        find_svg_url = re.search(r'span\[class\^="%s"\].*?background\-image: url\((.*?)\);' % _tag, con)
        if not find_svg_url:
            raise Exception("cannot find svg file, check")
        svg_url = find_svg_url.group(1)
        svg_url = "https:" + svg_url
        svg_content = self.session.get(svg_url).content
        svg_doc = H.document_fromstring(svg_content)
        datas = svg_doc.xpath("//text")
        # 把阈值和对应的数字集合放入一个字典中
        last = 0
        for index, data in enumerate(datas):
            y = int(data.xpath('@y')[0])
            int_set = data.xpath('text()')[0]
            index_and_word_dict[int_set] = range(last, y + 1)
            last = y
        return index_and_word_dict

    def get_shop_list(self, page):
        url = 'http://www.dianping.com/search/keyword/16/0_%s/p%d' % (self.keyword, page)
        page = self.session.get(url).content.decode('utf-8')
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
            # 获取css url，及tag
            css_url, _tag = self.get_css(content)
            # 获取css对应名与像素的映射
            css_and_px_dict = self.get_css_and_px_dict(css_url)
            # 获取svg的阈值与数字集合的映射
            svg_threshold_and_int_dict = self.get_svg_threshold_and_int_dict(css_url, _tag)

            shop_name = CrawlerUtils.get_tag(content, 'h1.shop-name')[0].text
            comment_list = CrawlerUtils.get_tag(content, 'li.comment-item')
            for comment in comment_list:
                username = comment.select('a.name')[0].text
                uuid = comment.attrs['data-id']

                is_vip = True if comment.find('span', {'class': 'vip'}) else False
                vip_level = 0
                if is_vip:
                    vip_img = comment.select('img.user-rank-rst')[0].attrs['src']
                    vip_level = vip_img.split('.')[-1]

                satrs = self.regex_findall(str(comment), 'sml-str(.*?) star')[0]

                messages = comment.select('div.content p.desc')
                msg = ''
                for message in messages.children:
                    if isinstance(message, str):
                        msg += message

                    else:
                        # span class的attr
                        span_class_attr_name = message.attrib["class"]
                        # 偏移量，以及所处的段
                        offset, position = css_and_px_dict[span_class_attr_name]
                        index = abs(int(float(offset)))
                        position = abs(int(float(position)))
                        # 判断
                        for key, value in svg_threshold_and_int_dict.items():
                            if position in value:
                                threshold = int(math.ceil(index / 12))
                                word = int(key[threshold - 1])
                                msg += msg + word

                comment_create_time = comment.find('span', {'class': 'time'}).text.strip()
                recommend = ','.join(list(map(lambda x: x.text, list(comment.find_all('a', {'class': 'col-exp'})))))
                # score = ','.join(list(map(lambda x: x.text.strip(), list(comment.find_all('span', 'item')))))

        except:
            return 0

    def run(self):
        for i in range(50):
            self.get_shop_list(i)
            time.sleep(2)


if __name__ == '__main__':
    DaZhongDianPing().run()
