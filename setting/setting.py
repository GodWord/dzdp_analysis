# -*- coding:utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:training@127.0.0.1/dzdp_db'

LOGIN_URL = 'https://account.dianping.com/login'

PROXIES_API_URL = 'http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=0&city=0&yys=0&port=1&pack=36593&ts=1&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions='

COOKIES = 'navCtgScroll=0; cy=9; cye=chongqing; _lxsdk_cuid=168fefecce9c8-0ade4a11c29357-b79183d-1fa400-168fefecce9c8; _lxsdk=168fefecce9c8-0ade4a11c29357-b79183d-1fa400-168fefecce9c8; _hc.v=629c0148-7004-8985-b305-0925333f6615.1550466338; ua=%E9%9B%A8; ctu=f8bbed2bbd7f3a4a99bc399c40df792f8b3262e0f2015d0e08918eb55d0e8b12; uamo=15870538863; s_ViewType=10; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; thirdtoken=4a61721c-f687-4b56-bf21-02325f88b469; dper=5e26184edae0cd1000ea0d5f05a6f9ab8db2f0f01217450dca34cd1bc663a5087e85fdf7420df71e9237520fd0ded0e534f131cc27af7c794334c2c427504db2292190e13e53caf3b63a130ed8c941e5c8a6e58007321d447e74cbfa61b4af7e; ll=7fd06e815b796be3df069dec7836c3df; ctu=cc3b1362586f16394d2c14472f23e99670f406595c9302f510edbdc9fc3de007380deb2dfc40b6524592d225f4a6e152; _lxsdk_s=16903337e71-399-535-f57%7C%7C131'
HEADERS = """Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding:gzip, deflate
Accept-Language:zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
Cache-Control:no-cache
Cookie:{}
Host:www.dianping.com
Pragma:no-cache
Proxy-Connection:keep-alive
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36
""".format(COOKIES)
