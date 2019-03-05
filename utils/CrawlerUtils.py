# -*- coding:utf-8 -*
import logging
import math
import re

import lxml.html as H
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('utils')
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.dianping.com',
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36",
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Cookie': '_lxsdk_cuid=168ff1b1f28c8-0530d22c516dd5-4313362-1fa400-168ff1b1f28c8; _lxsdk=168ff1b1f28c8-0530d22c516dd5-4313362-1fa400-168ff1b1f28c8; _hc.v=1fbb6612-4867-971e-f3e0-f654067f7ced.1550468194; s_ViewType=10; ua=dpuser_84171807103; ctu=63d65f0d1425edfa29563fb26d584e80c15f18d963633def6a89adea59e9c08b; dper=303e94eeb39c0d5bc3897c53b39c6022cd9263098a23e298bda93bc90beee886db69fb0354af62bf419882a2d1caf70107ab1123b14f3b6897794338913f5cebdc6f0989b7bce0279a32499a118748840f74a5aa92c96b0c649ee3683440909b; ll=7fd06e815b796be3df069dec7836c3df; aburl=1; cy=6; cye=suzhou; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=1693186dc03-eeb-f64-c4a%7C%7C616',
    'Proxy-Connection': 'keep-alive'
}

headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36",
    "Cookie": "cy=9; cye=chongqing; _lxsdk_cuid=168ff1b1f28c8-0530d22c516dd5-4313362-1fa400-168ff1b1f28c8; _lxsdk=168ff1b1f28c8-0530d22c516dd5-4313362-1fa400-168ff1b1f28c8; _hc.v=1fbb6612-4867-971e-f3e0-f654067f7ced.1550468194; s_ViewType=10; ua=dpuser_84171807103; ctu=63d65f0d1425edfa29563fb26d584e80c15f18d963633def6a89adea59e9c08b; dper=303e94eeb39c0d5bc3897c53b39c6022cd9263098a23e298bda93bc90beee886db69fb0354af62bf419882a2d1caf70107ab1123b14f3b6897794338913f5cebdc6f0989b7bce0279a32499a118748840f74a5aa92c96b0c649ee3683440909b; ll=7fd06e815b796be3df069dec7836c3df; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; _lxsdk_s=1690eee42f0-866-1d-f77%7C%7C1218"
}


class CrawlerUtils(object):
    @staticmethod
    def save_ing(browser):
        from selenium.webdriver import ActionChains
        from selenium.webdriver.common.keys import Keys
        element = browser.find_element_by_xpath('//*[@id="randCodeImg"]')
        print(element)

        # ActionChains(browser).context_click(element).send_keys('V').perform()

        action = ActionChains(browser).move_to_element('//*[@id="randCodeImg"]')  # 移动到该元素
        action.context_click()  # 右键点击该元素
        action.send_keys(Keys.ARROW_DOWN)  # 点击键盘向下箭头
        action.send_keys('v')  # 键盘输入V保存图
        action.perform()  # 执行保存
        print('保存成功')

    @staticmethod
    def convert_img(driver, img_location):
        import logging
        import os
        from PIL import Image
        tmp_path = './tmp'
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        driver.save_screenshot(os.path.join(tmp_path, 'code.png'))
        try:
            im = Image.open(os.path.join(tmp_path, 'code.png'))

            left = driver.find_element_by_xpath(img_location).location['x']
            top = driver.find_element_by_xpath(img_location).location['y']
            right = driver.find_element_by_xpath(img_location).location['x'] + \
                    driver.find_element_by_xpath(img_location).size['width']
            bottom = driver.find_element_by_xpath(img_location).location['y'] + \
                     driver.find_element_by_xpath(img_location).size['height']

            # 打开本地图片
            im = im.crop((left, top, right, bottom))
            im.save(os.path.join(tmp_path, 'screenshot.png'))
            print('screenshot.png 保存成功')
            os.remove(os.path.join(tmp_path, 'code.png'))
            return True
        except Exception as e:
            logging.error(e)
            return False

    @staticmethod
    def get_user_agent():
        import random
        user_agents = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
        ]
        return user_agents[random.randint(0, len(user_agents) - 1)]

    @staticmethod
    def get_headers(cookies):
        # headers = dict()
        headers2['User-Agent'] = CrawlerUtils.get_user_agent()
        headers2['Cookie'] = cookies
        return headers2

    @staticmethod
    def get_generator_by_csv(file_path: str, encoding='utf-8'):
        with open(file_path, 'r', encoding=encoding) as file:
            data = file.readlines()
        for values in data:
            keyword_list = values.strip().strip(',').split(',')
            if '' in keyword_list:
                keyword_list.remove('')
            for keyword in keyword_list:
                yield keyword

    @staticmethod
    def get_params_by_url(url):
        from urllib import parse
        params_url = parse.urlsplit(url).query
        params = dict(map(lambda x: x.split('='), params_url.split('&')))
        return params

    @staticmethod
    def get_tags(text, selector):
        from bs4 import BeautifulSoup
        bs = BeautifulSoup(text, 'lxml')
        res = bs.select(selector)
        return res

    @staticmethod
    def get_html(url, headers=None, params=None, is_post=False, **kwargs):
        import requests
        import logging

        if is_post:
            req = requests.post(url, headers=headers, params=params, **kwargs)
            req.encoding = req.apparent_encoding
        else:
            req = requests.get(url, headers=headers, params=params, **kwargs)
            req.encoding = req.apparent_encoding
        try:
            print(req.url)
            req.raise_for_status()
            return req.text
        except Exception as e:
            logging.error(e)
            return req.status_code

    @staticmethod
    def get_content(url, headers=None, params=None, is_post=False, **kwargs):
        import requests
        import logging

        if is_post:
            req = requests.post(url, headers=headers, params=params, **kwargs)
            req.encoding = req.apparent_encoding
        else:
            req = requests.get(url, headers=headers, params=params, **kwargs)
            req.encoding = req.apparent_encoding
        try:
            req.raise_for_status()
            return req.content
        except Exception as e:
            logging.error(e)
            return False

    @staticmethod
    def get_proxies(api_url):
        import json
        import requests
        import os

        # 代理服务器
        print('[%d]开始获取代理IP' % (os.getpid(),))
        data = json.loads(requests.get(api_url).content)
        if data['success'] == False:
            print('代理出现错误:%s' % (data['msg'],))
            return None
        proxy_host = data['data'][0]['ip']
        proxy_port = data['data'][0]['port']
        expire_time = data['data'][0]['expire_time']
        proxy_meta = "http://%(host)s:%(port)s" % {

            "host": proxy_host,
            "port": proxy_port,
        }
        proxies = {

            "http": proxy_meta,
            "https": proxy_meta,
        }
        print('[%d]获取代理IP成功,[%s],过期时间[%s]' % (os.getpid(), str(proxies), expire_time))
        return proxies

    @staticmethod
    def get_md5_value(value):
        import hashlib
        # 将字符串转成md5
        md5 = hashlib.md5()  # 获取一个MD5的加密算法对象
        md5.update(value.encode("utf8"))  # 得到MD5消息摘要
        md5_vlaue = md5.hexdigest()  # 以16进制返回消息摘要，32位
        return md5_vlaue

    @staticmethod
    def get_css_and_px_dict(css_url):
        """
        # 获取css对应名与像素的映射
        :param css_url:
        :param headers:
        :return:
        """
        con = requests.get(css_url, headers=headers2).content.decode("utf-8")
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

    @staticmethod
    def get_tag(_list, offset=1):
        _new_list = [data[0:offset] for data in _list]

        if len(set(_new_list)) == 1:
            # 说明全部重复
            offset += 1
            return CrawlerUtils.get_tag(_list, offset)
        else:
            _return_data = [data[0:offset - 1] for data in _list][0]

            return _return_data

    @staticmethod
    def get_css(content):
        matched = re.search(r'href="([^"]+svgtextcss[^"]+)"', content, re.M)
        if not matched:
            raise Exception("cannot find svgtextcss file")
        css_url = matched.group(1)
        css_url = "https:" + css_url
        return css_url

    @staticmethod
    def get_svg_threshold_and_int_dict(css_url, _add_res, _tag, is_num=True):
        con = requests.get(css_url, headers=headers2).content.decode("utf-8")
        index_and_word_dict = {}
        # 根据tag值匹配到相应的svg的网址
        find_svg_url = re.search(r'span\[class\^="%s"\].*?background\-image: url\((.*?)\);' % _tag, con)
        if not find_svg_url:
            raise Exception("cannot find svg file, check")
        svg_url = find_svg_url.group(1)
        svg_url = "https:" + svg_url
        svg_content = requests.get(svg_url, headers=headers2).content.decode('utf-8')
        last = 0
        if is_num:  # 当svg里面是数字时
            svg_doc = H.document_fromstring(svg_content)
            datas = svg_doc.xpath("//text")
            # 把阈值和对应的数字集合放入一个字典中
            for index, data in enumerate(datas):
                y = int(data.xpath('@y')[0])
                int_set = data.xpath('text()')[0]
                index_and_word_dict[int_set] = range(last, y + 1)
                last = y
            return index_and_word_dict
        else:  # 当svg里面是数字时
            svg_doc = BeautifulSoup(svg_content, "html.parser")
            all_y_values = svg_doc.findAll("path")
            all_y_dict = {}
            for _y in all_y_values:
                all_y_dict["#" + str(_y.attrs['id'])] = str(_y.attrs['d']).split(' ')[1]
            datas = svg_doc.findAll("textpath")  # svg_doc.xpath('.//span[@class="html-tag"]/text()') textpath
            for data in datas:
                y = int(all_y_dict[data.attrs['xlink:href']])
                int_set = data.text
                index_and_word_dict[int_set] = range(last, y + 1)
                last = y
            return index_and_word_dict

    @staticmethod
    def get_last_value(css_url, _add_res, css_and_px_dict, _tag, is_num=True):
        svg_threshold_and_int_dict = CrawlerUtils.get_svg_threshold_and_int_dict(css_url, _add_res, _tag, is_num=is_num)
        if svg_threshold_and_int_dict != {}:
            last_value = CrawlerUtils.get_svg_num(_add_res, css_and_px_dict, svg_threshold_and_int_dict, is_num=is_num)
            return last_value

    @staticmethod
    def get_bs(text, selector):
        from bs4 import BeautifulSoup
        bs = BeautifulSoup(text, 'lxml')
        res = bs.select(selector)
        return res

    @staticmethod
    def get_svg_num(datas, css_and_px_dict, svg_threshold_and_int_dict, is_num=True):
        num = ""
        if len(datas):
            for data in datas:
                # 如果是字符，则直接取出
                if isinstance(data, str):
                    num = num + data
                else:
                    # 如果是span类型，则要去找数据
                    # span class的attr
                    if not 'class' in data.attrib:
                        continue
                    span_class_attr_name = data.attrib["class"]
                    if span_class_attr_name == 'more-words':
                        num = num[:-3]
                        break
                    if span_class_attr_name == 'less-words':
                        break
                    if span_class_attr_name == 'emoji-img':
                        continue

                    # 偏移量，以及所处的段
                    offset, position = css_and_px_dict[span_class_attr_name]
                    index = abs(int(float(offset)))
                    position = abs(int(float(position)))
                    # 判断
                    for key, value in svg_threshold_and_int_dict.items():
                        if position in value:
                            threshold = int(math.ceil(index / 14))
                            if is_num:
                                number = key[threshold - 1]
                            else:
                                number = key[threshold]
                            num = num + str(number)
        else:
            return 0
        return num.strip()
