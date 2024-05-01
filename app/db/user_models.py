
from app.db.base_models import BaseTable
from app.db.base_models import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint
import uuid
from enum import Enum
from sqlalchemy import Enum as EnumColumn


class User(BaseTable):
    __tablename__ = 'users'

    username = Column(String(20), unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)
    member = relationship(
        'CompanyMember', back_populates='user',cascade='delete')
    actions = relationship('Action', back_populates='user')


class Company(BaseTable):
    __tablename__ = 'company'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    actions = relationship(
        'Action', back_populates='company', cascade='delete')
    members = relationship('CompanyMember', back_populates='company', cascade='delete')
    visible = Column(Boolean, default=True, nullable=False)

class Role(Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    MEMBER = 'member'

class CompanyMember(BaseTable):
    __tablename__ = 'company_members'

    company_id = Column(UUID(as_uuid=True), ForeignKey(
        'company.id',ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id',ondelete='CASCADE'), nullable=False)
    role = Column(EnumColumn(Role), nullable=False)
    company = relationship('Company', back_populates='members', cascade='delete')
    user = relationship('User', back_populates='member')

    __table_args__ = (UniqueConstraint('company_id', 'user_id', name='_company_user_uc'),)

class ActionStatus(Enum):
    INVITED = 'invited'
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'



class Action(BaseTable):
    __tablename__ = 'actions'

    status = Column(EnumColumn(ActionStatus), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey(
        'company.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    company = relationship(
        'Company', back_populates='actions', cascade='delete')
    user = relationship('User', back_populates='actions')
