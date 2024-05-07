from typing import List, Optional
from app.repositories.quiz_repository import QuizRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.quiz_shemas import QuizCreateSchema, QuizSchema, QuestionSchema, AnswerSchema, QuizResponseSchema, QuizUpdateSchema, QuestionResponseSchema, AnswerResponseSchema, QuizListSchema, ResultSchema
import bcrypt
from app.schemas.user_answer_schemas import AnswerQuestionListSchema, UserAnswerSchemaRedis
import logging
from fastapi import HTTPException
from app.db.user_models import User, Quiz, Question, Answer, Company, Result, UserAnswer
from uuid import UUID
from typing import Annotated
from app.auth.jwtauth import oauth2_scheme
from jose import jwt
from fastapi import Depends
from app.db.connect_postgresql import get_session
import aioredis
import json
from app.db.connect_redis import RedisClient
import asyncio
from app.core.config import Settings
import aioredis
import csv


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

    async def get_user_answers_by_result_id(self, result_id: UUID):
        user_answers = await self.quiz_repository.get_user_answers_by_result_id(result_id)
        return user_answers

    async def get_data_from_redis(self, key: str):
        redis_client = RedisClient()
        data = await redis_client.get_data(key)
        if data:
            data = json.loads(data)
            return data
        else:
            raise HTTPException(
                status_code=404, detail="Data not found in Redis")

    async def get_all_user_answer_records(self, user_id: UUID, quiz_id: UUID, type: str):
        redis_client = RedisClient()
        user_answer_records = []
        async for key in redis_client.scan_iter(f'user_answer:{user_id}:{quiz_id}:*'):
            data = await redis_client.get_data(key)
            data = json.loads(data)
            user_answer_records.append(data)
        if type == "csv":
            await self.save_user_answers_to_csv(user_answer_records)
        elif type == "json":
            await self.save_user_answers_to_json(user_answer_records)
        return user_answer_records

    async def save_user_answers_to_csv(self, user_answer_records: list):
        with open('user_answer_records.csv', 'w', newline='') as csvfile:
            fieldnames = user_answer_records[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for record in user_answer_records:
                writer.writerow(record)

    async def save_user_answers_to_json(self, user_answer_records: list):
        with open('user_answer_records.json', 'w') as jsonfile:
            json.dump(user_answer_records, jsonfile)
        

    async def save_user_answers_to_redis(self, result_id: UUID):
        redis_client = RedisClient()

        user_answer_list = await self.get_user_answers_by_result_id(result_id)
        redis_id = 0
        for user_answer in user_answer_list:
            user_answer_id = user_answer.answer_id
            user_answer_question_id = user_answer.question_id
            user_answer_result_id = result_id
            user_answer_user_id = await self.quiz_repository.get_user_id_by_result_id(user_answer_result_id)
            user_answer_quiz_id = await self.quiz_repository.get_quiz_id_by_result_id(user_answer_result_id)
            user_answer_company_id = await self.quiz_repository.get_company_id_by_quiz_id(user_answer_quiz_id)
            is_correct = await self.quiz_repository.check_if_user_answer_is_correct(user_answer_id, user_answer_question_id)

            save_data = {
                "question_id": str(user_answer_question_id),
                "answer_id": str(user_answer_id),
                "user_id": str(user_answer_user_id),
                "quiz_id": str(user_answer_quiz_id),
                "company_id": str(user_answer_company_id),
                "is_correct": is_correct
            }
            save_data = json.dumps(save_data)

            key = f"user_answer:{user_answer_user_id}:{user_answer_quiz_id}:{redis_id}"
            redis_id += 1
            await redis_client.set_data(key, save_data)
            logging.info(f"Data saved in Redis: {save_data}")

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
        await self.save_user_answers_to_redis(result_id)
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

    # be-14
    async def get_results_of_user_in_company(self, user_id: UUID, company_id: UUID, current_user: User):
        current_user_id = current_user.id
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, company_id)
        await self.check_if_user_member_of_company(user_id, company_id)
        quiz_ids_of_this_company = await self.quiz_repository.get_quiz_ids_of_company(company_id)
        user_result_all = []
        for quiz_id in quiz_ids_of_this_company:
            user_result = await self.get_user_results_of_quizzes_in_company(user_id, quiz_id)
            if user_result:
                user_result_all.append(user_result)
            if not user_result_all:
                raise HTTPException(
                    status_code=404, detail="Results not found for this user in")

        user_result_all = {"quiz_id": quiz_id, "quiz_results": user_result_all}

        return {"message": f"Results of user with id:{user_id} in company with id:{company_id}", "results": user_result_all}

    async def get_user_results_of_quizzes_in_company(self, user_id: UUID, quiz_id: UUID):
        redis_client = RedisClient()
        user_answer_records = []
        async for key in redis_client.scan_iter(f'user_answer:{user_id}:{quiz_id}:*'):
            data = await redis_client.get_data(key)
            data = json.loads(data)
            if data:
                user_answer_records.append(data)

        return user_answer_records

    async def get_results_of_all_users_in_quiz_id(self, quiz_id: UUID):
        redis_client = RedisClient()
        user_answer_records = []
        async for key in redis_client.scan_iter(f'user_answer:*:{quiz_id}:*'):
            data = await redis_client.get_data(key)
            data = json.loads(data)
            if data:
                user_answer_records.append(data)

        return user_answer_records

    async def get_results_of_all_users_in_company(self, company_id: UUID, current_user: User):
        current_user_id = current_user.id
        await self.check_if_user_is_admin_or_owner_in_company(current_user_id, company_id)
        quiz_ids_of_this_company = await self.quiz_repository.get_quiz_ids_of_company(company_id)
        all_results = []
        for quiz_id in quiz_ids_of_this_company:
            results = await self.get_results_of_all_users_in_quiz_id(quiz_id)
            if results:
                all_results.append(results)
        if not all_results:
            raise HTTPException(
                status_code=404, detail="Results not found for this company")

        return {"message": f"Results of all users in company with id:{company_id}", "results": all_results}
    

# be-15
    async def get_user_avarage_mark_from_all_quizzes(self,current_user_id: UUID):
        results = await self.quiz_repository.get_user_results_of_quizzes(current_user_id)
        if not results:
            raise HTTPException(
                status_code=404, detail="Results not found for you")
        sum_of_scores = 0
        quizzes = 0
        for result in results:
            sum_of_scores += result.score
            quizzes += 1
        avarage_mark = sum_of_scores/quizzes
        return {"message": f"Avarage mark from you", "avarage_mark": avarage_mark}