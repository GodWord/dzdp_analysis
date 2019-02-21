# -*- coding:utf-8 -*-
from datetime import datetime

from sqlalchemy import BigInteger, Column, Integer, String, BOOLEAN, DateTime, Text, SMALLINT, create_engine
from sqlalchemy.ext.declarative import declarative_base

from setting.setting import SQLALCHEMY_DATABASE_URI

Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URI, encoding="utf-8", echo=True)


class Comment(Base):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    __tablename__ = "comment"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    # 由shop_id+comment+comment_create_time三个字符串连接算出的MD5字段
    uuid = Column(String(32), nullable=True, unique=True, comment='唯一标识')
    shop_id = Column(BigInteger, nullable=True, index=True, comment='商家ID')
    username = Column(String(255), nullable=True, comment='商家名称')
    shop_name = Column(String(255), nullable=True, comment='商家名称')
    is_vip = Column(BOOLEAN, nullable=True, index=True, comment='是否为VIP')
    vip_level = Column(SMALLINT, nullable=True, default=0, index=True, comment='VIP等级')
    comment = Column(Text, nullable=True, comment='评论内容')
    recommend = Column(String(500), nullable=True, comment='推荐菜品')
    stars = Column(Integer, nullable=True, index=True, comment='用户评分')
    comment_create_time = Column(DateTime, nullable=True, comment='用户评论时间')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')


Base.metadata.create_all(engine)  # 创建表结构
