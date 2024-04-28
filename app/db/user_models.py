
from app.db.base_models import BaseTable
from app.db.base_models import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Boolean, ForeignKey
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
    companies = relationship('Company', back_populates='owner')
    invitations = relationship('Invitations', back_populates='user')



class Company(BaseTable):
    __tablename__ = 'company'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), default=uuid.uuid4, nullable=False)
    owner = relationship('User', back_populates='companies')
    members = relationship('Company_Members', back_populates='company')
    invitations = relationship('Invitations', back_populates='company')
    visible = Column(Boolean, default=True, nullable=False)


class Company_Members(BaseTable):
    __tablename__ = 'company_members'

    company_id = Column(UUID(as_uuid=True), ForeignKey(
        'company.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    company = relationship('Company', back_populates='members')
    
    


class InvitationStatus(Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    PROMOTED = 'promoted'

class Invitations(BaseTable):
    __tablename__ = 'invitations'
    
    status = Column(EnumColumn(InvitationStatus), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='invitations')
    company = relationship('Company', back_populates='invitations')




