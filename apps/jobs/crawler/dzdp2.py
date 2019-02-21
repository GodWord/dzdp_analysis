#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-12-5 上午10:54
# @Author  : ShiMeng
# @File    : dzdp.py
# @Software: PyCharm
import math
import re

import lxml.html as H
import requests
from lxml import etree
from selenium.webdriver import Chrome

# headers = {
#     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
# }
from setting.setting import HEADERS, LOGIN_URL, PROXIES_API_URL
from utils import CrawlerUtils


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

    def get_comment_msg(self, shop_link):
        com_con = self.session.get(shop_link).content.decode("utf-8")
        com_html = etree.HTML(com_con)
        # 获取css url，及tag
        css_url, _tag = self.get_css(com_con)
        # 获取css对应名与像素的映射
        css_and_px_dict = self.get_css_and_px_dict(css_url)
        # 获取svg的阈值与数字集合的映射
        svg_threshold_and_int_dict = self.get_svg_threshold_and_int_dict(css_url, _tag)

    def get_data(self, url):
        """
        :param page_url: 待获取url
        :return:
        """
        try:
            con = self.session.get(url).content.decode("utf-8")
            # 获取css url，及tag
            css_url, _tag = self.get_css(con)
            # 获取css对应名与像素的映射
            css_and_px_dict = self.get_css_and_px_dict(css_url)
            # 获取svg的阈值与数字集合的映射
            svg_threshold_and_int_dict = self.get_svg_threshold_and_int_dict(css_url, _tag)

            doc = etree.HTML(con)
            shops = doc.xpath('//div[@id="shop-all-list"]/ul/li')
            for shop in shops:
                # 店名
                name = shop.xpath('.//div[@class="tit"]/a')[0].attrib["title"]
                print(name)
                shop_link = shop.xpath('.//div[@class="tit"]/a')[0].attrib["href"] + "/review_all"
                print(self.session.get(shop_link))
                com_html = etree.HTML(self.session.get(url).content.decode("utf-8"))
                comment_num = 0
                price_num = taste = service = environment = 0

                # 获取点评总数
                comment_and_price_datas = shop.xpath('.//div[@class="comment"]')
                for comment_and_price_data in comment_and_price_datas:
                    _comment_data = comment_and_price_data.xpath('a[@class="review-num"]/b/node()')
                    # 遍历每一个node，这里node的类型不同，分别有etree._ElementStringResult(字符)，etree._Element（元素），etree._ElementUnicodeResult（字符）
                    for _node in _comment_data:
                        # 如果是字符，则直接取出
                        if isinstance(_node, str):
                            comment_num = comment_num * 10 + int(_node)
                        else:
                            # 如果是span类型，则要去找数据
                            # span class的attr
                            span_class_attr_name = _node.attrib["class"]
                            # 偏移量，以及所处的段
                            offset, position = css_and_px_dict[span_class_attr_name]
                            index = abs(int(float(offset)))
                            position = abs(int(float(position)))
                            # 判断
                            for key, value in svg_threshold_and_int_dict.items():
                                if position in value:
                                    threshold = int(math.ceil(index / 12))
                                    number = int(key[threshold - 1])
                                    comment_num = comment_num * 10 + number

                    # 获取人均消费价格
                    _price = comment_and_price_data.xpath('a[@class="mean-price"]/b/node()')
                    for price_node in _price:
                        if isinstance(price_node, str):
                            if len(price_node) > 1:
                                price_num = price_num * 10 + int(price_node[1:])
                        elif isinstance(price_node, etree._ElementStringResult):
                            price_num = price_num * 10 + int(price_node)
                        else:
                            span_class_attr_name = price_node.attrib["class"]
                            # 偏移量，以及所处的段
                            offset, position = css_and_px_dict[span_class_attr_name]
                            index = abs(int(float(offset)))
                            position = abs(int(float(position)))
                            # 判断
                            for key, value in svg_threshold_and_int_dict.items():
                                if position in value:
                                    threshold = int(math.ceil(index / 12))
                                    number = int(key[threshold - 1])
                                    price_num = price_num * 10 + number

                # 获取口味，环境，服务评分
                others_num_node = shop.xpath('.//span[@class="comment-list"]/span')
                for others_datas in others_num_node:
                    if others_datas.xpath('text()') and others_datas.xpath('text()')[0] == u"口味":
                        _taste_data = others_datas.xpath('b/node()')
                        for _taste in _taste_data:
                            if isinstance(_taste, etree._Element):
                                css_class = _taste.attrib["class"]
                                # 偏移量，以及所处的段
                                offset, position = css_and_px_dict[css_class]
                                index = abs(int(float(offset)))
                                position = abs(int(float(position)))
                                # 判断
                                for key, value in svg_threshold_and_int_dict.items():
                                    if position in value:
                                        threshold = int(math.ceil(index / 12))
                                        number = int(key[threshold - 1])
                                        taste = taste * 10 + number
                            else:
                                if len(_taste) > 1:  #
                                    taste = taste * 10 + int(_taste[1:])
                        taste = round(taste / 10, 1)

                    if others_datas.xpath('text()') and others_datas.xpath('text()')[0] == u"服务":
                        _taste_data = others_datas.xpath('b/node()')
                        for _taste in _taste_data:
                            if isinstance(_taste, etree._Element):
                                css_class = _taste.attrib["class"]
                                # 偏移量，以及所处的段
                                offset, position = css_and_px_dict[css_class]
                                index = abs(int(float(offset)))
                                position = abs(int(float(position)))
                                # 判断
                                for key, value in svg_threshold_and_int_dict.items():
                                    if position in value:
                                        threshold = int(math.ceil(index / 12))
                                        number = int(key[threshold - 1])
                                        service = service * 10 + number
                            else:
                                if len(_taste) > 1:  #
                                    service = service * 10 + int(_taste[1:])
                        service = round(service / 10, 1)

                    if others_datas.xpath('text()') and others_datas.xpath('text()')[0] == u"环境":
                        _taste_data = others_datas.xpath('b/node()')
                        for _taste in _taste_data:
                            if isinstance(_taste, etree._Element):
                                css_class = _taste.attrib["class"]
                                offset, position = css_and_px_dict[css_class]
                                index = abs(int(float(offset)))
                                position = abs(int(float(position)))
                                # 判断
                                for key, value in svg_threshold_and_int_dict.items():
                                    if position in value:
                                        threshold = int(math.ceil(index / 12))
                                        number = int(key[threshold - 1])
                                        environment = environment * 10 + number
                            else:
                                if len(_taste) > 1:
                                    environment = environment * 10 + int(_taste[1:])
                        environment = round(environment / 10, 1)

                print("restaurant: {}\n, "
                      "comment total num: {}\n, "
                      "price num: {}\n,"
                      "taste score:{}\n,"
                      "service socre:{}\n, "
                      "environment_score:{}, "
                      "\n ".
                      format(bytes(name.encode('utf-8')).decode('utf-8'), comment_num, price_num, taste, service,
                             environment))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # http://www.dianping.com/suzhou/ch10/g110p3
    url = "https://www.dianping.com/suzhou/ch10/g110"
    dp = DZDP('农家乐')
    dp.get_data(url)
