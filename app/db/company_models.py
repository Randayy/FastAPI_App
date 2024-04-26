from sqlalchemy import Column, String, Boolean,ForeignKey
from app.db.base_models import BaseTable
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Company(BaseTable):
    __tablename__ = 'company'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    owner_id = Column(UUID(as_uuid=True),ForeignKey('users.id') ,default=uuid.uuid4, nullable=False)
    owner = relationship('User', back_populates='companies')
    visible = Column(Boolean, default=True)
