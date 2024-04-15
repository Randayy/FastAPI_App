from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseTable(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
class User(BaseTable):
    __tablename__ = 'users'

    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)