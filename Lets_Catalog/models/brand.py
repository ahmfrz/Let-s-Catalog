"""Defines Brand table"""

import datetime
from database_setup import Base
from user import User
from subcategory import SubCategory
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship

class Brand(Base):
    ''' Defines brand table and columns '''

    __tablename__ = "brand"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'))
    subcategory = relationship(SubCategory)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'subcategory_id': self.subcategory_id
        }