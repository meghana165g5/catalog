import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class Login_User(Base):
    __tablename__ = 'userlogin'

    id = Column(Integer, primary_key=True)
    gmail = Column(String, nullable=False)


class Mobile_Category(Base):
    __tablename__ = 'mobile_category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    id_user = Column(Integer, ForeignKey('userlogin.id'))
    user = relationship(Login_User)


class Menu_Items(Base):
    __tablename__ = 'menu_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(300))
    price = Column(String(8))
    brand = Column(String(8))
    image = Column(String(300))
    mobile_category_id = Column(Integer, ForeignKey('mobile_category.id'))
    Mobile_Category = relationship(
        Mobile_Category, backref=backref("menu_item", cascade="all,delete"))

    @property
    def serialise(self):
        data = {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'brand': self.brand,
            'image': self.image}
        return data

engine = create_engine('sqlite:///mobile.db')
Base.metadata.create_all(engine)
