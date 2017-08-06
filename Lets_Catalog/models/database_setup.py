"""Defines database setup"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# Create an instance of declarative base
Base = declarative_base()

# Create postgres engine for db
connectionString = 'postgresql://{}:{}@{}:{}/{}'
connectionString = connectionString.format('catalog', 'pw', 'localhost', 5432, 'catalogdb')
engine = create_engine(connectionString)

#from product_pics import *
#from product_specs import *
#from product import *
#from brand import *
#from subcategory import *
#from category import *
#from user import *

# Create all tables
Base.metadata.create_all(engine)
