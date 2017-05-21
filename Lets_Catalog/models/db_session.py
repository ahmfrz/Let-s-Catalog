"""Creates database session"""

from database_setup import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Create connection with the database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

make_session = sessionmaker(bind=engine)
dbsession = make_session()