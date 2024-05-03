from typing import List, Optional
from app.repositories.quiz_repository import QuizRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.quiz_shemas import QuizCreateSchema, QuizSchema, QuestionSchema, AnswerSchema, QuizResponseSchema, QuizUpdateSchema, QuestionResponseSchema, AnswerResponseSchema, QuizListSchema, ResultSchema
import bcrypt
from app.schemas.user_answer_schemas import AnswerQuestionListSchema
import logging
from fastapi import HTTPException
from app.db.user_models import User, Quiz, Question, Answer, Company, Result
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

    async def check_if_user_member_of_company(self, current_user: UUID, company_id: UUID):
        await self.quiz_repository.check_if_user_member_of_company(current_user, company_id)

    async def create_quiz(self, quiz_data: QuizCreateSchema, current_user: User, company_id: UUID) -> QuizSchema:
        current_user_id = current_user.id
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, company_id)
        quiz_dict = await self.quiz_repository.create_quiz(quiz_data.dict(), company_id)
        quiz_id = quiz_dict['id']
        # List[QuestionSchema]
        questions = await self.get_quiz_questions(quiz_id)
        quiz_response = QuizResponseSchema(
            quiz_info=quiz_dict, questions=questions)
        return quiz_response

    async def delete_quiz(self, quiz_id: UUID, current_user: User) -> str:
        current_user_id = current_user.id
        quiz = await self.quiz_repository.get_quiz_by_id(quiz_id)
        quiz_company_id = quiz['company_id']
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, quiz_company_id)
        await self.quiz_repository.delete_quiz(quiz_id)
        return {"message": "Quiz deleted"}

    async def update_quiz(self, quiz_data: QuizUpdateSchema, quiz_id: UUID, current_user: User) -> QuizSchema:
        current_user_id = current_user.id
        quiz = await self.quiz_repository.get_quiz_by_id(quiz_id)
        quiz_company_id = quiz['company_id']
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, quiz_company_id)
        quiz_dict = await self.quiz_repository.update_quiz(quiz_id, quiz_data.dict())
        quiz_id = quiz_dict['id']
        # List[QuestionSchema]
        questions = await self.get_quiz_questions(quiz_id)
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


# be-12

    async def check_if_user_alredy_submitted_quiz(self, current_user_id: UUID, quiz_id: UUID):
        result = await self.quiz_repository.check_if_user_alredy_submitted_quiz(current_user_id, quiz_id)
        return result

    async def submit_quiz_answers(self, user_answers: AnswerQuestionListSchema, company_id: UUID, quiz_id: UUID, current_user: User):
        current_user_id = current_user.id
        await self.check_if_user_member_of_company(current_user_id, company_id)
        check = await self.check_if_user_alredy_submitted_quiz(current_user_id, quiz_id)
        if check:
            raise HTTPException(
                status_code=400, detail="You already submitted this quiz")
        await self.quiz_repository.check_if_quiz_exists(quiz_id)
        question_ids_list = await self.quiz_repository.if_questions_exists_get_questions_ids_list(quiz_id)
        questions_answers_list_dicts = await self.quiz_repository.get_questions_answers_list_dicts(question_ids_list)

        user_answers_list_dicts = user_answers.dict()
        user_answers = user_answers_list_dicts['questions_answers']
        user_answers_list_ids = [ans['answer_id']
                                 for answer in user_answers for ans in answer['answers']]

        correct_answers = 0
        questions = 0
        for question_answers in questions_answers_list_dicts:
            for question_answer in question_answers:
                if question_answer['is_correct'] and question_answer['id'] in user_answers_list_ids:
                    correct_answers += 1
            questions += 1

        result = await self.quiz_repository.submit_quiz_result(correct_answers, questions, quiz_id, current_user_id)
        result_id = result.id
        result_score = result.score
        await self.quiz_repository.save_user_answers(user_answers, result_id)
        return {"message": "Quiz submitted successfully", "score": result_score}

    async def get_quiz_results(self, company_id: UUID, quiz_id: UUID, current_user: User) -> ResultSchema:
        current_user_id = current_user.id
        await self.check_if_user_member_of_company(current_user_id, company_id)
        quiz = await self.quiz_repository.get_quiz_by_id(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        result = await self.check_if_user_alredy_submitted_quiz(current_user_id, quiz_id)
        if not result:
            raise HTTPException(
                status_code=400, detail="You have not submitted this quiz yet")
        result = await self.quiz_repository.get_quiz_results_for_user(quiz_id, current_user_id)
        return ResultSchema(**result.__dict__)

    async def get_user_avarage_mark_from_quizzes(self, user_id: UUID, current_user: User):
        current_user_id = current_user.id
        if current_user_id != user_id:
            raise HTTPException(
                status_code=401, detail="You are not this user to get this information")
        results = await self.quiz_repository.get_user_results_of_quizzes(user_id)
        sum_of_scores = 0
        quizzes = 0
        for result in results:
            sum_of_scores += result.score
            quizzes += 1
        avarage_mark = sum_of_scores/quizzes
        return {"message": f"Avarage mark from quizzes for user with id:{user_id}", "avarage_mark": avarage_mark}

    async def get_user_avarage_mark_from_quizzes_in_company(self, user_id: UUID, company_id: UUID, current_user: User):
        current_user_id = current_user.id
        await self.check_if_user_member_of_company(current_user_id, company_id)
        if current_user_id != user_id:
            raise HTTPException(
                status_code=401, detail="You are not this user to get this information")
        results = await self.quiz_repository.get_user_results_of_quizzes_in_company(company_id, user_id)
        sum_of_scores = 0
        quizzes = 0
        for result in results:
            sum_of_scores += result.score
            quizzes += 1
        avarage_mark = sum_of_scores/quizzes
        return {"message": f"Avarage mark from quizzes for user with id:{user_id} in company with id:{company_id}", "avarage_mark": avarage_mark}
