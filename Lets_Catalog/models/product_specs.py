"""Defines product specification table"""

from product import Product
from database_setup import Base
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

class Product_Specs(Base):
    ''' Defines product specs table and columns '''

    __tablename__ = "product_specs"

    id = Column(Integer, primary_key=True)
    model_number = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    color = Column(String(50), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship(Product, backref=backref(
        "specs", cascade="all, delete-orphan"))
