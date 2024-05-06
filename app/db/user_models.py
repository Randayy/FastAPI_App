
from app.db.base_models import BaseTable
from app.db.base_models import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint, Integer, Float, DateTime
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
        'CompanyMember', back_populates='user', cascade='delete')
    actions = relationship('Action', back_populates='user')


class Company(BaseTable):
    __tablename__ = 'company'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    actions = relationship(
        'Action', back_populates='company', cascade='delete')
    members = relationship(
        'CompanyMember', back_populates='company', cascade='delete')
    visible = Column(Boolean, default=True, nullable=False)
    quizzes = relationship('Quiz', back_populates='company', cascade='delete')


class Role(Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    MEMBER = 'member'


class CompanyMember(BaseTable):
    __tablename__ = 'company_members'

    company_id = Column(UUID(as_uuid=True), ForeignKey(
        'company.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    role = Column(EnumColumn(Role), nullable=False)
    company = relationship(
        'Company', back_populates='members', cascade='delete')
    user = relationship('User', back_populates='member')

    __table_args__ = (UniqueConstraint(
        'company_id', 'user_id', name='_company_user_uc'),)


class ActionStatus(Enum):
    INVITED = 'invited'
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'

class ExportType(Enum):
    CSV = 'csv'
    JSON = 'json'


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


class Quiz(BaseTable):
    __tablename__ = 'quizzes'

    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    frequency_days = Column(Integer, nullable=False)
    questions = relationship(
        'Question', back_populates='quiz', cascade='delete')
    company_id = Column(UUID(as_uuid=True), ForeignKey(
        'company.id', ondelete='CASCADE'), nullable=False)
    company = relationship('Company', back_populates='quizzes')


class Question(BaseTable):
    __tablename__ = 'questions'

    question_text = Column(String(255), nullable=False)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey(
        'quizzes.id', ondelete='CASCADE'), nullable=False)
    quiz = relationship('Quiz', back_populates='questions')
    answers = relationship(
        'Answer', back_populates='question', cascade='delete')


class Answer(BaseTable):
    __tablename__ = 'answers'

    answer_text = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey(
        'questions.id', ondelete='CASCADE'), nullable=False)
    question = relationship('Question', back_populates='answers')


class Result(BaseTable):
    __tablename__ = 'results'

    quiz_id = Column(UUID(as_uuid=True), ForeignKey(
        'quizzes.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    quiz = relationship('Quiz')
    user = relationship('User')


class UserAnswer(BaseTable):
    __tablename__ = 'user_answer'

    result_id = Column(UUID(as_uuid=True), ForeignKey(
        'results.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey(
        'questions.id', ondelete='CASCADE'), nullable=False)
    answer_id = Column(UUID(as_uuid=True), ForeignKey(
        'answers.id', ondelete='CASCADE'), nullable=False)
    result = relationship('Result')
    question = relationship('Question')
    answer = relationship('Answer')
