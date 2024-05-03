from pydantic import BaseModel, validator
from typing import List, Optional
from pydantic.fields import Field
from uuid import UUID


class AnswerSchema(BaseModel):
    answer_text: str
    is_correct: bool

    class Config:
        from_attributes=True

class AnswerResponseSchema(AnswerSchema):
    id:UUID

class QuestionSchema(BaseModel):
    question_text: str
    answers: List[AnswerSchema]
 

    class Config:
        from_attributes=True
    
    @validator('answers')
    def check_correct_answer(cls, answers, values, **kwargs):
        if not any(answer.is_correct for answer in answers):
            raise ValueError('No correct answer provided.')
        return answers
    
class QuestionResponseSchema(QuestionSchema):
    id:UUID
    answers: List[AnswerResponseSchema]
    
class QuestionUpdateSchema(BaseModel):
    question_text: str
    answers: List[AnswerResponseSchema]
 

    class Config:
        from_attributes=True
    
    @validator('answers')
    def check_correct_answer(cls, answers, values, **kwargs):
        if not any(answer.is_correct for answer in answers):
            raise ValueError('No correct answer provided.')
        return answers


class QuizSchema(BaseModel):
    title: str
    description: Optional[str] = None
    frequency_days: int
    
    class Config:
        from_attributes=True
    
class QuizResponseSchema(BaseModel):
    quiz_info: QuizSchema
    questions: List[QuestionResponseSchema]

    @validator('questions')
    def validate_questions(cls, questions):
        if len(questions) < 2:
            raise ValueError("Quiz must have at least two questions.")
        return questions
    
    
    class Config:
        from_attributes=True

    
class AnswerCreateSchema(AnswerSchema):
    pass

class QuestionCreateSchema(QuestionSchema):
    pass

class QuizCreateSchema(BaseModel):
    title: str
    description: Optional[str] = None
    frequency_days: int 
    questions: List[QuestionSchema]

    @validator('questions')
    def validate_questions(cls, questions):
        if len(questions) < 2:
            raise ValueError("Quiz must have at least two questions.")
        return questions
    
    class Config:
        from_attributes=True

class QuizUpdateSchema(BaseModel):
    title: str
    description: Optional[str] = None
    frequency_days: int
    questions: List[QuestionResponseSchema]

    @validator('questions')
    def validate_questions(cls, questions):
        if len(questions) < 2:
            raise ValueError("Quiz must have at least two questions.")
        return questions

    class Config:
        from_attributes=True

class QuizListSchema(BaseModel):
    quizzes: List[QuizSchema]

    class Config:
        from_attributes=True

class QuestionListSchema(BaseModel):
    questions: List[QuestionResponseSchema]

    class Config:
        from_attributes=True
    
class AnswerListSchema(BaseModel):
    answers: List[AnswerResponseSchema]

    class Config:
        from_attributes=True

class ResultSchema(BaseModel):
    quiz_id: UUID
    user_id: UUID
    score: float

    class Config:
        from_attributes=True