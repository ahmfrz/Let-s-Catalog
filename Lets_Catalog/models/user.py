"""Defines user table"""

from database_setup import Base
from sqlalchemy import Column, String, Integer

class User(Base):
    ''' Defines product specs table and columns '''

    __tablename__ = 'cataloguser'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(250))