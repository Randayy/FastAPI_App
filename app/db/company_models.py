from sqlalchemy import Column, String, Boolean
from app.db.base_models import BaseTable
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Company(BaseTable):
    __tablename__ = 'company'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    owner_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    visible = Column(Boolean, default=True)
