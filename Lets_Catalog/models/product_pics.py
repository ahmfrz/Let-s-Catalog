"""Defines product pics table"""

from database_setup import Base
from product import Product
from sqlalchemy import Column, ForeignKey, Integer, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

class Product_Pics(Base):
    ''' Defines product pics table and columns '''

    __tablename__ = "product_pics"

    id = Column(Integer, primary_key=True)
    picture = Column(TEXT)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship(Product, backref=backref(
        "pics", cascade="all, delete-orphan"))