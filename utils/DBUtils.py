# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from setting.setting import DB_SOURCE

__author__ = 'zhoujifeng'
__date__ = '2019/2/22 9:41'


class DBUtils:
    @staticmethod
    def get_session():
        """
        通过model获取session
        :return:
        """
        SessionCls = sessionmaker(
            bind=create_engine(DB_SOURCE['default'], pool_size=1000, pool_recycle=3600, echo=True, max_overflow=-1))
        New_SessionCls = scoped_session(SessionCls)
        session = New_SessionCls()
        return session

    @staticmethod
    def save_to_db(model, data, filter):
        try:
            print(data)
            session = DBUtils.get_session()
            session.add(model(**data))
            session.commit()
        except Exception as e:
            print(e)
