# -*- coding:utf-8 -*-
import math
import re
import time

import lxml.html as H
import requests
from selenium.webdriver import Chrome

from apps.models import Comment, Shop
from setting.setting import PROXIES_API_URL, LOGIN_URL, SEARCH_KEYWORD
from utils import CrawlerUtils
from utils.DBUtils import DBUtils
from utils.DPUtils import DPUtils


class DaZhongDianPing:

    def __init__(self, keyword):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CrawlerUtils.get_user_agent()
        })
        self.max_comment_page = 8
        self.session.proxies = CrawlerUtils.get_proxies(PROXIES_API_URL)

        self.keyword = keyword
        self.get_cookies(LOGIN_URL)
        self.session.verify = False

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

    def get_css(self, content, compile):
        matched = re.search(r'href="([^"]+svgtextcss[^"]+)"', content, re.M)
        if not matched:
            raise Exception("cannot find svgtextcss file")
        css_url = matched.group(1)

        css_url = "https:" + css_url

        class_tag = re.findall(compile, content)
        tags = list()
        list(map(lambda x: tags.append(x) if len(x) == 5 else '', class_tag))
        _tag = self.get_tag(tags)

        return css_url, _tag

    def get_word_css(self, content, compile):
        matched = re.search(r'href="([^"]+svgtextcss[^"]+)"', content, re.M)
        if not matched:
            raise Exception("cannot find svgtextcss file")
        css_url = matched.group(1)

        css_url = "https:" + css_url
        span_tags = re.findall("<span class=\"(.*?)\"></span>", content)
        class_tag = list()
        list(map(lambda x: class_tag.append(x) if len(x) == 5 else '', span_tags))
        _tag = self.get_tag(class_tag)

        return css_url, _tag

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

    def svg(self, html, comp):
        # 获取css url,及tag
        css_url, _tag = self.get_css(html, comp)
        # 获取css对应名与像素的映射
        css_and_px_dict = self.get_css_and_px_dict(css_url)
        # 获取svg的阈值与数字集合的映射
        svg_threshold_and_int_dict = self.get_svg_threshold_and_int_dict(css_url, _tag)
        return css_and_px_dict, svg_threshold_and_int_dict

    def get_shop_list(self, page):
        url = 'https://www.dianping.com/search/keyword/9/10_%s/p%d' % (self.keyword, page)
        con = '未请求页面！！！'
        try:
            print(url)
            con = self.session.get(url).content.decode("utf-8")

            shops = CrawlerUtils.get_tag(con, 'div.shop-list li')
            addr_css_and_px_dict, addr_svg_threshold_and_int_dict = self.svg(con, '<span class=\"(mc.*?)\"></span>')
            for shop in shops:
                # 店名
                shop_name = shop.select('h4')[0].text
                stars = shop.select('span.sml-rank-stars')[0].attrs['class'][-1].split('sml-str')[-1]
                shop_id = shop.select('div.tit a')[0].attrs["data-shopid"]
                addr_tags = shop.select('span.addr')
                address = DPUtils.get_real_by_tag(addr_tags[0].children, addr_css_and_px_dict,
                                                  addr_svg_threshold_and_int_dict)

                num_css_and_px_dict, num_svg_threshold_and_int_dict = self.svg(con, '<b><span class=\"(.*?)\"></span>')

                # 获取点评总数
                review_num_tags = shop.select('a.review-num b')
                total_number_comments = DPUtils.get_real_by_tag(review_num_tags[0].children, num_css_and_px_dict,
                                                                num_svg_threshold_and_int_dict, diff=-1)

                # 获取人均价格
                mean_price_tags = shop.select('a.mean-price b')
                if mean_price_tags:
                    per_capita_price = DPUtils.get_real_by_tag(mean_price_tags[0].children, num_css_and_px_dict,
                                                               num_svg_threshold_and_int_dict, diff=-1)[1:]
                else:
                    per_capita_price = 0

                if shop.select('span.comment-list'):
                    comment_list_tags = shop.select('span.comment-list b')
                    # 获取口味评分
                    taste = DPUtils.get_real_by_tag(comment_list_tags[0].children, num_css_and_px_dict,
                                                    num_svg_threshold_and_int_dict, diff=-1)
                    # 获取环境评分
                    surroundings = DPUtils.get_real_by_tag(comment_list_tags[1].children, num_css_and_px_dict,
                                                           num_svg_threshold_and_int_dict, diff=-1)
                    # 获取服务评分
                    serve = DPUtils.get_real_by_tag(comment_list_tags[2].children, num_css_and_px_dict,
                                                    num_svg_threshold_and_int_dict, diff=-1)
                else:
                    taste = 0
                    serve = 0
                    surroundings = 0

                data = {
                    'shop_id': shop_id,
                    'shop_name': shop_name,
                    'address': address,
                    'per_capita_price': per_capita_price,
                    'total_number_comments': total_number_comments,
                    'stars': int(stars),
                    'taste': taste,
                    'surroundings': surroundings,
                    'serve': serve,
                }
                DBUtils.save_to_db(Shop, data, 'shop_id')
                self.get_comment(shop_id)
        except Exception as e:
            if re.search(r'验证中心', con):
                self.session.proxies = CrawlerUtils.get_proxies(PROXIES_API_URL)
                page -= 1
            else:
                print('----------------------------------ERROR HTML START----------------------------------')
                print(con)
                print('----------------------------------ERROR HTML END----------------------------------')
                raise e

    def get_real_word(self, tags, css_and_px_dict, svg_threshold_and_int_dict):
        msg = ''
        for tag in tags:
            if isinstance(tag, str):
                msg += tag.strip().replace('\n', '').replace('\r', '')
            else:
                # span class的attr
                if not 'class' in tag.attrs:
                    continue
                span_class_attr_name = tag.attrs["class"][0]
                if span_class_attr_name == 'more-words':
                    msg = msg[:-3]
                    break
                if len(span_class_attr_name) != 5:
                    continue
                # 偏移量，以及所处的段
                offset, position = css_and_px_dict[span_class_attr_name]
                index = abs(int(float(offset)))
                position = abs(int(float(position)))
                # 判断
                for key, value in svg_threshold_and_int_dict.items():
                    if position in value:
                        threshold = int(math.ceil(index / 14))
                        word = key[threshold]
                        msg += word
        return msg

    def get_comment(self, shop_id):
        page = 0
        while True:
            page += 1
            content = '未请求页面！！！'
            try:
                url = 'http://www.dianping.com/shop/%s/review_all/p%d' % (shop_id, page)
                print(url)
                content = self.session.get(url).content.decode()

                css_and_px_dict, svg_threshold_and_int_dict = self.svg(content, '<span class=\"(.*?)\"></span>')
                shop_name = CrawlerUtils.get_tag(content, 'h1.shop-name')[0].text
                main_review = CrawlerUtils.get_tag(content, 'div.main-review')
                for comment in main_review:
                    username = comment.select('.name')[0].text.strip().strip('\n').strip('\r')

                    is_vip = True if comment.find('span', {'class': 'vip'}) else False
                    vip_level = 0
                    if is_vip:
                        vip_img = comment.select('img.user-rank-rst')[0].attrs['src']
                        vip_level = vip_img.split('squarelv')[-1][0]

                    stars = self.regex_findall(str(comment), 'sml-str(.*?) star')[0]

                    review_truncated_words = comment.select('div.review-truncated-words')
                    if review_truncated_words.__len__() == 0:
                        review_truncated_words = comment.select('div.review-words')
                        review_words_hide = ''
                    else:
                        review_words_hide = review_truncated_words[0].next_sibling.next_sibling

                    msg = self.get_real_word(review_truncated_words[0].children, css_and_px_dict,
                                             svg_threshold_and_int_dict)
                    if not isinstance(review_words_hide, str):
                        msg += self.get_real_word(review_words_hide.children, css_and_px_dict,
                                                  svg_threshold_and_int_dict)

                    comment_create_time = comment.find('span', {'class': 'time'}).text.strip().strip('\n').strip('\r')
                    recommend = ','.join(list(map(lambda x: x.text, list(comment.find_all('a', {'class': 'col-exp'})))))
                    uuid = CrawlerUtils.get_md5_value(str(shop_id) + msg + str(comment_create_time))
                    data = {
                        'uuid': uuid,
                        'shop_id': int(shop_id),
                        'shop_name': shop_name,
                        'username': username,
                        'is_vip': is_vip,
                        'vip_level': int(vip_level),
                        'stars': int(stars),
                        'comment': msg,
                        'comment_create_time': comment_create_time,
                        'recommend': recommend,
                    }
                    DBUtils.save_to_db(Comment, data, 'uuid')
                    del data
                if not CrawlerUtils.get_tag(content, 'a.NextPage'):
                    return
            except Exception as e:
                if re.search(r'验证中心', content):
                    self.session.proxies = CrawlerUtils.get_proxies(PROXIES_API_URL)
                    page -= 1
                else:
                    print('----------------------------------ERROR HTML START----------------------------------')
                    print(content)
                    print('----------------------------------ERROR HTML END----------------------------------')

                    raise e

    def run(self):
        for i in range(50):
            self.get_shop_list(i)
            time.sleep(2)


if __name__ == '__main__':
    DaZhongDianPing(SEARCH_KEYWORD).run()
