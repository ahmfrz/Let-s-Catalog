"""Defines subcategory table"""

import datetime
from database_setup import Base
from category import Category
from user import User
#from database_setup import Base
from sqlalchemy import Column, String, ForeignKey, Integer, TEXT, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

class SubCategory(Base):
    ''' Defines sub category table and columns '''

    __tablename__ = "subcategory"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(TEXT)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, backref=backref(
        "subs", cascade="all, delete-orphan"))
    user_id = Column(Integer, ForeignKey('cataloguser.id'))
    user = relationship(User)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id
        }
