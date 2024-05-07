from pydantic import BaseModel, validator
from typing import List, Optional
from pydantic.fields import Field
from uuid import UUID


class UserAnswerSchema(BaseModel):
    answer_id: UUID

    class Config:
        from_attributes=True

class AnswerQuestionSchema(BaseModel):
    question_id: UUID
    answers: List[UserAnswerSchema]

    class Config:
        from_attributes=True

class AnswerQuestionListSchema(BaseModel):
    questions_answers: List[AnswerQuestionSchema]

    class Config:
        from_attributes=True

class UserAnswerSchemaRedis(BaseModel):
    question_id: UUID
    answer_id: UUID
    user_id: UUID
    quiz_id: UUID
    company_id: UUID
    is_correct: bool

    class Config:
        from_attributes=True