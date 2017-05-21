"""Defines category table"""

import datetime
from database_setup import Base
from user import User
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship

class Category(Base):
    ''' Defines category table and columns '''

    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }