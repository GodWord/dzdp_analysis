# -*- coding:utf-8 -*
import logging

logger = logging.getLogger('utils')


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
    def get_headers(str_headers):
        headers = dict(map(lambda x: x.split(':', 1), str_headers.strip().split('\n')))
        headers['User-Agent'] = CrawlerUtils.get_user_agent()
        return headers

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
    def get_tag(text, selector):
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
