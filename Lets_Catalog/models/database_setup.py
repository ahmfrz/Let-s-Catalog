"""Defines database setup"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# Create an instance of declarative base
Base = declarative_base()

# Create sqlite engine for simple local db
engine = create_engine("sqlite:///catalog.db")

# Create all tables
Base.metadata.create_all(engine)