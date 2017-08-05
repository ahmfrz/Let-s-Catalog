"""Defines product table"""

import datetime
from database_setup import Base
from user import User
from subcategory import SubCategory
from brand import Brand
from sqlalchemy import Column, String, ForeignKey, Integer, TEXT, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

class Product(Base):
    ''' Defines product table and columns '''

    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(TEXT, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'))
    subcategory = relationship(SubCategory, backref=backref(
        "products", cascade="all, delete-orphan"))
    brand_id = Column(Integer, ForeignKey('brand.id'))
    brand = relationship(Brand)
    user_id = Column(Integer, ForeignKey('cataloguser.id'))
    user = relationship(User)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'brand_id': self.brand_id,
            'subcategory_id': self.subcategory_id
        }