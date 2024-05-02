from typing import List, Optional
from app.repositories.quiz_repository import QuizRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.quiz_shemas import QuizCreateSchema, QuizSchema, QuestionSchema, AnswerSchema, QuizResponseSchema, QuizUpdateSchema, QuestionResponseSchema, AnswerResponseSchema, QuizListSchema
import bcrypt
import logging
from fastapi import HTTPException
from app.db.user_models import User, Quiz
from uuid import UUID
from typing import Annotated
from app.auth.jwtauth import oauth2_scheme
from jose import jwt
from fastapi import Depends
from app.db.connect_postgresql import get_session


class QuizService:
    def __init__(self, db: AsyncSession):
        self.quiz_repository = QuizRepository(db)

    async def get_quiz_by_id(self, quiz_id: UUID, current_user: User) -> QuizSchema:
        await self.check_if_user_is_owner_or_admin_in_this_quiz_company_by_quiz_id(current_user, quiz_id)
        quiz = await self.quiz_repository.get_quiz_by_id(quiz_id)
        return QuizSchema(**quiz)

    async def get_quiz_by_id_full_info(self, quiz_id: UUID, current_user: User) -> QuizResponseSchema:
        await self.check_if_user_is_owner_or_admin_in_this_quiz_company_by_quiz_id(current_user, quiz_id)
        quiz = await self.quiz_repository.get_quiz_by_id(quiz_id)
        questions = await self.get_quiz_questions(quiz_id)
        quiz_response = QuizResponseSchema(quiz_info=quiz, questions=questions)
        return quiz_response

    async def get_quiz_questions(self, quiz_id: UUID):
        questions = await self.quiz_repository.get_quiz_questions(quiz_id)
        list_questions = []
        for question in questions:
            question_id = question['id']
            answers = await self.get_question_answers(question_id)
            question['answers'] = answers
            list_questions.append(question)

        return [QuestionResponseSchema(**question) for question in list_questions]

    async def check_if_user_is_owner_or_admin_in_this_quiz_company_by_quiz_id(self, current_user: User, quiz_id: UUID):
        current_user_id = current_user.id
        await self.quiz_repository.check_if_user_is_owner_or_admin_in_this_quiz_company_by_quiz_id(current_user_id, quiz_id)

    async def get_quiz_questions_to_response(self, quiz_id: UUID, current_user: User):
        await self.check_if_user_is_owner_or_admin_in_this_quiz_company_by_quiz_id(current_user, quiz_id)
        questions = await self.quiz_repository.get_quiz_questions(quiz_id)
        list_questions = []
        for question in questions:
            question_id = question['id']
            answers = await self.get_question_answers_to_response(question_id, current_user)
            question['answers'] = answers
            list_questions.append(question)

        return [QuestionResponseSchema(**question) for question in list_questions]

    async def check_if_user_is_owner_or_admin_in_this_quiz_company(self, current_user: User, question_id: UUID):
        current_user_id = current_user.id
        await self.quiz_repository.check_if_user_is_owner_or_admin_in_this_quiz_company(current_user_id, question_id)

    async def get_question_answers(self, question_id: UUID) -> List[AnswerResponseSchema]:
        answers = await self.quiz_repository.get_question_answers(question_id)
        return [AnswerResponseSchema(**answer) for answer in answers]

    async def get_question_answers_to_response(self, question_id: UUID, current_user: UUID) -> List[AnswerResponseSchema]:
        await self.check_if_user_is_owner_or_admin_in_this_quiz_company(current_user, question_id)
        answers = await self.quiz_repository.get_question_answers(question_id)
        return [AnswerResponseSchema(**answer) for answer in answers]

    async def check_if_user_is_admin_or_owner_in_company(self, current_user: UUID, company_id: UUID):
        await self.quiz_repository.check_if_user_is_admin_or_owner_in_company(current_user, company_id)

    async def create_quiz(self, quiz_data: QuizCreateSchema, current_user: User, company_id: UUID) -> QuizSchema:
        current_user_id = current_user.id
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, company_id)
        quiz_dict = await self.quiz_repository.create_quiz(quiz_data.dict(), company_id)
        quiz_id = quiz_dict['id']
        questions = await self.get_quiz_questions(quiz_id) # List[QuestionSchema]
        quiz_response = QuizResponseSchema(
            quiz_info=quiz_dict, questions=questions)
        return quiz_response

    async def delete_quiz(self, quiz_id: UUID, current_user: User) -> str:
        current_user_id = current_user.id
        quiz = await self.quiz_repository.get_quiz_by_id(quiz_id)
        quiz_company_id = quiz['company_id']
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, quiz_company_id)
        await self.quiz_repository.delete_quiz(quiz_id)
        return {"message":"Quiz deleted"}

    async def update_quiz(self, quiz_data: QuizUpdateSchema, quiz_id: UUID, current_user: User) -> QuizSchema:
        current_user_id = current_user.id
        quiz = await self.quiz_repository.get_quiz_by_id(quiz_id)
        quiz_company_id = quiz['company_id']
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, quiz_company_id)
        quiz_dict = await self.quiz_repository.update_quiz(quiz_id, quiz_data.dict())
        quiz_id = quiz_dict['id']
        questions = await self.get_quiz_questions(quiz_id) # List[QuestionSchema]
        quiz_response = QuizResponseSchema(
            quiz_info=quiz_dict, questions=questions)
        return quiz_response

    async def list_quizzes(self, company_id: UUID, current_user: User, page: int, limit: int) -> QuizListSchema:
        current_user_id = current_user.id
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, company_id)
        current_user_id = current_user.id
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, company_id)
        quizzes = await self.quiz_repository.list_quizzes(company_id, page, limit)
        return [QuizSchema(**quiz) for quiz in quizzes]
