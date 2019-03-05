# -*- coding:utf-8 -*-
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from setting.setting import DB_SOURCE

logger = logging.getLogger('dp')


class DBUtils:
    @staticmethod
    def get_session():
        """
        获取数据库session
        :return:session
        """
        # 根据setting配置获取session
        SessionCls = sessionmaker(
            bind=create_engine(DB_SOURCE['default'], pool_size=1000, pool_recycle=3600, echo=True, max_overflow=-1))
        New_SessionCls = scoped_session(SessionCls)
        session = New_SessionCls()
        return session

    @staticmethod
    def save_to_db(model, data):
        try:
            logger.info(data)
            # 获取session
            session = DBUtils.get_session()
            # 在session中添加数据
            session.add(model(**data))
            # commit(这里不提交数据库是不会保存的)
            session.commit()
        except Exception as e:
            # 由于对数据进行了唯一字段设置，当出现数据重复时会报错
            logger.info(e)
