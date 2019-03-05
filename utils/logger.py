# -*- coding:utf8 -*-
import logging
import os


class Logger(object):

    def __init__(self, level=logging.DEBUG, filename='log/all.log', filemode='a', datefmt='%a, %d %b %Y %H:%M:%S',
                 format='%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d]  %(message)s'):
        if not os.path.exists(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])
        # 配置日志信息
        logging.basicConfig(level=level,
                            format=format,
                            datefmt=datefmt,
                            filename=filename,
                            filemode=filemode)
        # 定义一个Handler打印INFO及以上级别的日志到sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # 设置日志打印格式
        formatter = logging.Formatter(format)
        console.setFormatter(formatter)
        # 将定义好的console日志handler添加到root logger
        logging.getLogger('').addHandler(console)
