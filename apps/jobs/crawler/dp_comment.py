# coding: utf-8
import re
from time import sleep

import requests
from lxml import etree
from pyquery import PyQuery as pq

from apps.models import Comment
from utils.CrawlerUtils import CrawlerUtils
from utils.DBUtils import DBUtils

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.dianping.com',
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
    'Cookie': 'cy=9; cye=chongqing; _lxsdk_cuid=1694b61416cc8-09fe474311d39b-9333061-1fa400-1694b61416cc8; _lxsdk=1694b61416cc8-09fe474311d39b-9333061-1fa400-1694b61416cc8; _hc.v=2404787b-97c0-ccde-445a-50d86ce42194.1551747859; s_ViewType=10; dper=bf3c7459819f47e4d850b04f3d13b4b9b8b97298115bc7c9baa7bef9cf988c702f712274c541ee0964c5383400645fd34eb2d918677aeab0a1bce4126aa163553c54b0140f00ea9c76f4799b3f70f0313ecea5f5fa914cc259bb8d3a5d0623bd; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_84171807103; ctu=63d65f0d1425edfa29563fb26d584e80e6610cf7dff2f468ee94cd3924bfba4a; uamo=17723776773; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=1694b61416d-1c1-537-481%7C%7C501'
}


def spiderDazhong(shop_id, now_page):
    global page
    global proxies
    try:
        url = "http://www.dianping.com/shop/" + str(shop_id) + "/review_all/p" + str(now_page)
        print("url==========", url)
        req = requests.get(url, headers=headers)  # , proxies=proxies
        if CrawlerUtils.get_bs(req.text, 'div#log'):
            proxies = CrawlerUtils.get_proxies(api_url)
            page -= 1
            return True
        # 获取svg的阈值与数字集合的映射
        css_url = CrawlerUtils.get_css(req.content.decode('utf-8'))
        str_re_compile = '<span class=\"(.*?)\"></span>'
        addr_tag = CrawlerUtils.get_bs(req.text, 'div.review-truncated-words')

        if addr_tag != []:
            addr_tag = str(addr_tag[0])
        else:

            addr_tag = str(CrawlerUtils.get_bs(req.text, 'div.review-words')[0])

        _tag = CrawlerUtils.get_tag(re.findall(str_re_compile, addr_tag))
        css_and_px_dict = CrawlerUtils.get_css_and_px_dict(css_url)

        doc = pq(req.text)
        # print(doc)
        if doc:
            # # 存入csv文件
            # out = open('./data/Stu_csv.csv', 'a', newline='', encoding="utf-8")
            # # 设定写入模式
            # csv_write = csv.writer(out, dialect='excel')
            # shopName = doc("div.review-list-header > h1 > a").text()
            # shopurl = "http://www.dianping.com" + doc("div.review-list-header > h1 > a").attr("href")
            # csv_write.writerow(["店铺名称", "店铺网址"])
            # csv_write.writerow([shopName, shopurl])
            # csv_write.writerow(["用户名", "用户ID链接", "评定星级", "评论描述", "评论详情", "评论时间", "评论商铺", "评论图片","是否VIP","推荐菜品"])
            # 解析评论
            pinglunLi = doc("div.reviews-items > ul > li").items()
            li_num = 1
            for data in pinglunLi:
                userName = data("div.main-review > div.dper-info > a").text()  # 用户名
                shopName = data("div.main-review > div.misc-info.clearfix > span.shop").text()  #

                userID = ''
                user_id_link = data("div.main-review > div.dper-info > a").attr("href")
                if user_id_link != None:
                    userID = "http://www.dianping.com" + user_id_link

                start_sapn = data("div.review-rank > span.sml-rank-stars.sml-str10.star")
                if start_sapn:
                    startShop = str(start_sapn.attr("class")).split(" ")[1].replace("sml-str", "")
                else:
                    startShop = 0

                describeShop = data("div.review-rank > span.score").text()
                msg_values = etree.HTML(req.content.decode('utf-8')).xpath('//div[@class="reviews-items"]/ul/li[' + str(
                    li_num) + ']/div[@class="main-review"]/div[@class="review-words Hide"]/node()')  #
                if msg_values == []:
                    msg_values = etree.HTML(req.content.decode('utf-8')).xpath(
                        '//div[@class="reviews-items"]/ul/li[' + str(
                            li_num) + ']/div[@class="main-review"]/div[@class="review-words"]/node()')
                pinglunShop = CrawlerUtils.get_last_value(css_url, msg_values, css_and_px_dict, _tag, is_num=False)
                if pinglunShop == '':
                    continue
                timeShop = data("div.main-review > div.misc-info.clearfix > span.time").text()
                Shop = data("div.main-review > div.misc-info.clearfix > span.shop").text()
                imgShop = data("div > div.review-pictures > ul > li> a").items()
                imgList = []
                for img in imgShop:
                    imgList.append("http://www.dianping.com" + img.attr("href"))
                vip_span = data("div.main-review > div.dper-info > span")
                is_vip = 1 if vip_span.attr("class") == "vip" else 0
                recommend = data("div.main-review > div.review-recommend > a").text()
                print("===========", pinglunShop)
                uuid = CrawlerUtils.get_md5_value(str(shop_id) + pinglunShop + str(timeShop))

                # # 写入具体内容
                # csv_write.writerow([userName, userID, startShop, describeShop, pinglunShop, timeShop, Shop, imgList])
                # print("successful insert csv!")
                print(", 用户名：userName: {}\n, "
                      "商铺名称：shoName: {}\n, "
                      "用户ID链接：userID: {}\n, "
                      "评定星级：startShop: {}\n, "
                      "评论描述：describeShop : {}\n, "
                      "星级评分：startShop: {}\n, "
                      "评论详情：pinglunShop:{}\n, "
                      "评论时间：timeShop :{}\n, "
                      "评论商铺：Shop:{}\n, "
                      "评论图片：imgList:{}\n, "
                      "推荐菜品：recommend:{}\n, "
                      "是否vip：is_vip:{} "
                      "\n ".
                      format(userName, shopName, userID, startShop, describeShop, startShop, pinglunShop, timeShop,
                             Shop,
                             imgList, recommend, is_vip))

                data = {
                    'uuid': uuid,
                    'shop_id': shop_id,
                    'username': userName,
                    'shop_name': shopName,
                    'is_vip': is_vip,
                    'comment': pinglunShop,
                    'recommend': recommend,
                    'stars': startShop,
                    'comment_create_time': timeShop,
                }
                DBUtils.save_to_db(Comment, data)
                li_num += 1
                sleep(1)
            if not CrawlerUtils.get_tags(req.text, '.NextPage'):
                return False

            return True

    except Exception as e:
        raise e


if __name__ == '__main__':
    # 代表各大商铺ID，可通过商铺列表页回去
    api_url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=0&city=0&yys=0&port=1&time=1&ts=1&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions='
    proxies = CrawlerUtils.get_proxies(api_url)
    page = 194
    listShop = ["4718470"]
    # listShop = [
    #             '14172218',
    #             '65573626',
    #             '93404805',
    #             '17872711',
    #             '98797092',
    #             '5391378',
    #             '4887202',
    #             '112061816',
    #             '32475784',
    #             '91598186',
    #             '5706062',
    #             '5494165',
    #             '65703219',
    #             '23112913',
    #             '93293593',
    #             '4732159',
    #             '69737098',
    #             '18100522',
    #             '95243981',
    #             '92811890',
    #             '5101297',
    #             '76742010',
    #             '97488828',
    #             '5708930',
    #             '24332703',
    #             '21691356',
    #             '15109058',
    #             '18176551',
    #             '2048647',
    #             '3631459',
    #             '66449162',
    #             '92684951',
    #             '93000923',
    #             '5668668',
    #             '3452665',
    #             '124120444',
    #             '8858095',
    #             '21316222',
    #             '32654769',
    #             '4233103',
    #             '59447195',
    #             '3341992',
    #             '57092409',
    #             '4550679',
    #             '9046003',
    #             '21814522',
    #             '23975351',
    #             '28597600',
    #             '22816979',
    #             '69438623',
    #             '5217857',
    #             '5175995',
    #             '93313072',
    #             '66053429',
    #             '67280401',
    #             '21651979',
    #             '5151960',
    #             '22392346',
    #             '5256485',
    #             '56776131',
    #             '75686581',
    #             '37765199',
    #             '112288343',
    #             '22801006',
    #             '2089273',
    #             '20903440',
    #             '95358871',
    #             '21953390',
    #             '14162777',
    #             '98250813',
    #             '18667032',
    #             '6112021',
    #             '98827700',
    #             '48229846',
    #             '2433064',
    #             '68920752',
    #             '93251063',
    #             '32400848',
    #             '38217557',
    #             '69750425',
    #             '19594961',
    #             '18070549',
    #             '70764578',
    #             '95518289',
    #             '4733904',
    #             '5493505',
    #             '69587559',
    #             '98759670',
    #             '65635930',
    #             '67244182',
    #             '23900827',
    #             '3384271',
    #             '94304219',
    #             '19635271',
    #             '5419724',
    #             '5277599',
    #             '3104989',
    #             '68015252',
    #             '23754821',
    #             '11571334',
    #             '80234128',
    #             '58193701',
    #             '15031540',
    #             '19276913',
    #             '24811571',
    #             '58631614',
    #             '14745843',
    #             '13783468',
    #             '83443093',
    #             '102288563',
    #             '76718130',
    #             '14752049',
    #             '110551301',
    #             '26214436',
    #             '108159923',
    #             '82245756',
    #             '5535666',
    #             '16813672',
    #             '21651105',
    #             '23024868',
    #             '70127980',
    #             '24955310',
    #             '3120667',
    #             '18228133',
    #             '22583294',
    #             '58595101',
    #             '76875199',
    #             '21809213',
    #             '67579050',
    #             '96190270',
    #             '563199',
    #             '18514953',
    #             '9203138',
    #             '67185404',
    #             '23883922',
    #             '92226833',
    #             '18098909',
    #             '32335915',
    #             '110735852',
    #             '5986969',
    #             '76951598',
    #             '48138056',
    #             '68148250',
    #             '23630568',
    #             '6076948',
    #             '19194396',
    #             '6077037',
    #             '93866227',
    #             '13668451',
    #             '8711436',
    #             '10724103',
    #             '32708897',
    #             '93078604',
    #             '20834890',
    #             '110075164',
    #             '15090104',
    #             '17798382',
    #             '82867780',
    #             '101979248',
    #             '4696395',
    #             '21648138',
    #             '8880931',
    #             '27454563',
    #             '124563989',
    #             '21101507',
    #             '91671379',
    #             '27316933',
    #             '69004526',
    #             '122054340',
    #             '5490747',
    #             '6456644',
    #             '3220684',
    #             '69700825',
    #             '83297405',
    #             '67145376',
    #             '23129697',
    #             '106430142',
    #             '2623825',
    #             '44371286',
    #             '98914138',
    #             '126158302',
    #             '97872537',
    #             '10389787',
    #             '9196875',
    #             '9245297',
    #             '80223419',
    #             '65958408',
    #             '67195468',
    #             '92442481',
    #             '32592708',
    #             '15905718',
    #             '95388683',
    #             '9084981',
    #             '6091922',
    #             '98910471',
    #             '9081673',
    #             ]
    for shop in listShop:
        while True:
            if spiderDazhong(shop, page):
                page += 1
            else:
                break
