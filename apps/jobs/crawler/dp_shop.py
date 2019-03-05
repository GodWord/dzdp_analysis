import logging
import math
import re

import lxml.html as H
import requests
from bs4 import BeautifulSoup
from lxml import etree

from apps.models import Shop
from setting.setting import COOKIES
from utils import CrawlerUtils
from utils.DBUtils import DBUtils
from utils.logger import Logger

logger = logging.getLogger('dp_shop')


def get_class_name(class_content):
    """

    :param class_content:
    :return:
    """
    _list = list()
    if class_content:
        for class_name in class_content:
            if not isinstance(class_name, str):
                _list.append(class_name.attrib["class"])
    return _list


def get_tag(_list, offset=1):
    _new_list = [data[0:offset] for data in _list]

    if len(set(_new_list)) == 1:
        # 说明全部重复
        offset += 1
        return get_tag(_list, offset)
    else:
        _return_data = [data[0:offset - 1] for data in _list][0]

        return _return_data


def get_css(content):
    """
    用正则匹配网页中的css文件的url
    :param content: 网页HTML结构
    :return: CSS的URL
    """
    matched = re.search(r'href="([^"]+svgtextcss[^"]+)"', content, re.M)
    if not matched:
        raise Exception("cannot find svgtextcss file")
    css_url = matched.group(1)

    css_url = "https:" + css_url
    return css_url


def get_svg_threshold_and_int_dict(css_url, _add_res, _tag, is_num=True):
    con = requests.get(css_url, headers=CrawlerUtils.get_headers(COOKIES)).content.decode("utf-8")
    index_and_word_dict = {}
    # 根据tag值匹配到相应的svg的网址
    find_svg_url = re.search(r'span\[class\^="%s"\].*?background\-image: url\((.*?)\);' % _tag, con)
    if not find_svg_url:
        raise Exception("cannot find svg file, check")
    svg_url = find_svg_url.group(1)
    svg_url = "https:" + svg_url
    svg_content = requests.get(svg_url, headers=CrawlerUtils.get_headers(COOKIES)).content
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


def get_css_and_px_dict(css_url):
    con = requests.get(css_url, headers=CrawlerUtils.get_headers(COOKIES)).content.decode("utf-8")
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
                span_class_attr_name = data.attrib["class"]
                # 偏移量，以及所处的段
                offset, position = css_and_px_dict[span_class_attr_name]
                index = abs(int(float(offset)))
                position = abs(int(float(position)))
                # 判断
                for key, value in svg_threshold_and_int_dict.items():
                    if position in value:
                        threshold = int(math.ceil(index / 12))
                        if is_num:
                            number = key[threshold - 1]
                        else:
                            number = key[threshold]
                        num = num + str(number)
    else:
        return 0
    return num


def get_last_value(css_url, _add_res, css_and_px_dict, _tag, is_num=True):
    # 获取svg的阈值与数字集合的映射
    svg_threshold_and_int_dict = get_svg_threshold_and_int_dict(css_url, _add_res, _tag, is_num=is_num)
    if svg_threshold_and_int_dict != {}:
        last_value = get_svg_num(_add_res, css_and_px_dict, svg_threshold_and_int_dict, is_num=is_num)
        return last_value


def get_data(url):
    """
    :param page_url: 待获取url
    :return:
    """
    try:
        # 获取url中的html文本
        con = CrawlerUtils.get_html(url, headers=CrawlerUtils.get_headers(COOKIES), proxies=proxies)
        # 获取css url，及tag，由于文本与数字class 前缀不同，所以需要分别获取
        num_re_compile = "<b><span class=\"(.*?)\"></span>"  # 定义数字class匹配正则
        str_re_compile = '<span class="addr"><span class=\"(.*?)\"></span>'  # 定义地址class匹配正则
        # 获取css的URL
        css_url = get_css(con)
        # 获取数字class前缀
        num_svg_tag = get_tag(re.findall(num_re_compile, con))
        # 获取文本class前缀
        str_svg_tag = get_tag(re.findall(str_re_compile, con))
        # 获取css对应名与像素的映射字典
        css_and_px_dict = get_css_and_px_dict(css_url)
        # 对html文本使用 etree.HTML(html)解析，得到Element对象
        doc = etree.HTML(con)
        # 获取所有商家标签
        shops = doc.xpath('//div[@id="shop-all-list"]/ul/li')
        for shop in shops[1:]:
            # 商铺id
            shop_id = shop.xpath('.//div[@class="tit"]/a')[0].attrib["data-shopid"]
            logger.info("shop_id", shop_id)
            # 店名
            shop_name = shop.xpath('.//div[@class="tit"]/a')[0].attrib["title"]
            shop_name = bytes(shop_name.encode('utf-8')).decode('utf-8')

            comment_num = 0
            per_capita_price = taste = service = environment = 0

            # 获取星级评分数
            star_num = int(str(shop.xpath('.//div[@class="comment"]/span')[0].attrib["class"]).split("sml-str")[-1])
            # 获取点评总数
            comment_and_price_datas = shop.xpath('.//div[@class="comment"]')
            for comment_and_price_data in comment_and_price_datas:
                _comment_data = comment_and_price_data.xpath('a[@class="review-num"]/b/node()')
                comment_num = get_last_value(css_url, _comment_data, css_and_px_dict, num_svg_tag)
                comment_num = int(comment_num) if comment_num else 0
                if comment_num == 0:
                    return

                # 获取人均消费价格
                _price = comment_and_price_data.xpath('a[@class="mean-price"]/b/node()')
                per_capita_price = get_last_value(css_url, _price, css_and_px_dict, num_svg_tag)
                per_capita_price = int(per_capita_price[1:]) if per_capita_price else 0

            # 获取口味，环境，服务评分
            others_num_node = shop.xpath('.//span[@class="comment-list"]/span')
            for others_datas in others_num_node:
                if others_datas.xpath('text()') and others_datas.xpath('text()')[0] == u"口味":
                    _taste_data = others_datas.xpath('b/node()')
                    taste = get_last_value(css_url, _taste_data, css_and_px_dict, num_svg_tag)
                    taste = float(taste) if taste else 0

                if others_datas.xpath('text()') and others_datas.xpath('text()')[0] == u"服务":
                    _taste_data = others_datas.xpath('b/node()')
                    service = get_last_value(css_url, _taste_data, css_and_px_dict, num_svg_tag)
                    service = float(service) if service else 0

                if others_datas.xpath('text()') and others_datas.xpath('text()')[0] == u"环境":
                    _taste_data = others_datas.xpath('b/node()')
                    environment = get_last_value(css_url, _taste_data, css_and_px_dict, num_svg_tag)
                    environment = float(environment) if environment else 0

            # 获取地址
            _ress = shop.xpath('.//div[@class="tag-addr"]/span[@class="addr"]/node()')
            address = get_last_value(css_url, _ress, css_and_px_dict, str_svg_tag, is_num=False)

            data = {
                'shop_id': shop_id,
                'shop_name': shop_name,
                'address': address,
                'per_capita_price': per_capita_price,
                'total_number_comments': comment_num,
                'stars': int(star_num),
                'taste': taste,
                'surroundings': environment,
                'serve': service,
            }
            logger.info('开始保存数据: %s' % (data,))
            # 保存数据
            DBUtils.save_to_db(Shop, data)

    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    # 日志系统初始化
    Logger()
    # 代理URL (这里用的是芝麻代理，代理封IP 封的很快，所以可以用自己的IP，然后换cookies,也可以用重启猫来更换IP)
    api_url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=0&city=0&yys=0&port=1&pack=36593&ts=1&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions='
    # 需要爬取的URL {}是需要拼装的数据
    url = "http://www.dianping.com/search/keyword/{}/10_%E5%86%9C%E5%AE%B6%E4%B9%90%E7%BE%8E%E9%A3%9F/p{}"
    # 获取代理
    # proxies = CrawlerUtils.get_proxies(api_url)
    proxies = None
    # 城市ID
    city_ids = [12, ]
    for city in city_ids:
        # 由于大部分城市偏后的商家评论数量不多或没有评论，所有只对需要爬取城市前10页商家进行抓取
        for page in range(1, 11):
            # 组装URL
            now_url = url.format(city, page, )
            # 输出日志
            logger.info("开始请求:[%s]" % (now_url,))
            # 开始获取数据
            get_data(now_url)
