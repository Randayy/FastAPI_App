from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseTable(Base):
    # __abstract__ = True
    __tablename__ = 'base_table'

    id = Column(Integer, primary_key=True, index=True)

