from sqlalchemy import Column, Integer, String
from app.db.base_models import BaseTable
from sqlalchemy.sql.schema import CheckConstraint
from sqlalchemy.sql import func
class User(BaseTable):
    __tablename__ = 'users'
    
    username = Column(String(20), unique=True, index=True,nullable=False)
    password = Column(String,nullable=False)
    email = Column(String(100), unique=True, index=True,nullable=False)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)

    __table_args__ = (
        CheckConstraint(func.char_length(username) >= 5, name='username_min_length'),
        CheckConstraint(func.char_length(password) >= 8, name='password_min_length'),
    )
