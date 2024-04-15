from sqlalchemy import Column, Integer, String
from app.db.base_models import BaseTable

class User(BaseTable):
    __tablename__ = 'users'

    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)