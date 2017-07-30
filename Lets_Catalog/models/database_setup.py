"""Defines database setup"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# Create an instance of declarative base
Base = declarative_base()

# Create postgres engine for db
connectionString = 'postgresql://{}:{}@{}:{}/{}'
connectionString = connectionString.format('catalogdb', '12345', 'localhost', 5432, 'catalogdb')
engine = create_engine(connectionString)

# Create all tables
Base.metadata.create_all(engine)