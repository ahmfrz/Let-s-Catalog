"""Creates database session"""

from database_setup import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Create connection with the database
connectionString = 'postgresql://{}:{}@{}:{}/{}'
connectionString = connectionString.format('admin', '12345', '127.0.0.1', '5432', 'catalogdb')
engine = create_engine(connectionString)
Base.metadata.bind = engine

make_session = sessionmaker(bind=engine)
dbsession = make_session()