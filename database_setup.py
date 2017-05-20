""" The product specs entity """

import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, TEXT, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Create an instance of declarative base
Base = declarative_base()


class User(Base):
    ''' Defines product specs table and columns '''

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(250))

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


class SubCategory(Base):
    ''' Defines sub category table and columns '''

    __tablename__ = "subcategory"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(TEXT(500))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    def serialize(self):
        return {
        'id': self.id,
        'name': self.name,
        'description': self.description,
        'category_id':self.category_id
        }


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
        'subcategory_id' : self.subcategory_id
        }


class Product(Base):
    ''' Defines product table and columns '''

    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(TEXT(500), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'))
    subcategory = relationship(SubCategory)
    brand_id = Column(Integer, ForeignKey('brand.id'))
    brand = relationship(Brand)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    def serialize(self):
        return {
        'id': self.id,
        'name': self.name,
        'description' : self.description,
        'brand_id' : self.brand_id,
        'subcategory_id' : self.subcategory_id
        }

class Product_Pics(Base):
    ''' Defines product pics table and columns '''

    __tablename__ = "product_pics"

    id = Column(Integer, primary_key=True)
    picture = Column(TEXT(250))
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship(Product)


class Product_Specs(Base):
    ''' Defines product specs table and columns '''

    __tablename__ = "product_specs"

    id = Column(Integer, primary_key=True)
    model_number = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    color = Column(String(50), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship(Product)

# Create sqlite engine for simple local db
engine = create_engine("sqlite:///catalog.db")

# Create all tables
Base.metadata.create_all(engine)
