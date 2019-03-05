# -*- coding:utf-8 -*-
from datetime import datetime

from sqlalchemy import BigInteger, Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base

from setting.setting import DB_SOURCE

Base = declarative_base()

engine = create_engine(DB_SOURCE['default'], encoding="utf-8", echo=True)


class Shop(Base):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    __tablename__ = "shop"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    shop_id = Column(BigInteger, nullable=True, index=True, unique=True, comment='商家ID')
    shop_name = Column(String(255), nullable=True, comment='商家名称')
    address = Column(String(500), nullable=True, default='未知', comment='地址')
    per_capita_price = Column(Integer, nullable=True, default=0, comment='人均价格')
    total_number_comments = Column(Integer, nullable=True, default=0, comment='评论总数')
    stars = Column(Integer, nullable=True, index=True, comment='店铺评分')
    taste = Column(Integer, nullable=True, index=True, comment='口味评分')
    surroundings = Column(Integer, nullable=True, index=True, comment='环境评分')
    serve = Column(Integer, nullable=True, index=True, comment='服务评分')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')


Base.metadata.create_all(engine)  # 创建表结构
