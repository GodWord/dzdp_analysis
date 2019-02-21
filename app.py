# -*- coding:utf-8 -*-
from apps.jobs.crawler.dzdp import DZDP
from utils import CrawlerUtils

__author__ = 'zhoujifeng'
__date__ = '2019/2/15 23:12'
import apps.models

if __name__ == '__main__':
    try:
        url = 'https://account.dianping.com/login'
        key_word = '农家乐'
        dp = DZDP(key_word)
        dp.run()
    except Exception as e:
        print(e)
