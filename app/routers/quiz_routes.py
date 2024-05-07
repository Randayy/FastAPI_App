from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connect_postgresql import get_session
from app.db.connect_redis import RedisClient
from fastapi import APIRouter, HTTPException, status

from app.db.user_models import User, Company
from app.schemas.user_answer_schemas import AnswerQuestionListSchema
from app.schemas.quiz_shemas import QuizCreateSchema, QuizUpdateSchema, QuizResponseSchema, QuizSchema, AnswerListSchema, QuestionListSchema, QuizListSchema
from app.services.quiz_service import QuizService
from app.services.user_service import get_current_user_from_token
from uuid import UUID
from typing import List

quiz_router = APIRouter(tags=["Quizzes"])


@quiz_router.post("/quizzes/{company_id}/create", response_model=QuizResponseSchema)
async def create_quiz(company_id: UUID, quiz_data: QuizCreateSchema, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.create_quiz(quiz_data, current_user, company_id)
    return result


@quiz_router.get("/quizzes/{quiz_id}", response_model=QuizSchema)
async def get_quiz_by_id(quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_quiz_by_id(quiz_id, current_user)
    return result


@quiz_router.get("/quizzes/{quiz_id}/full", response_model=QuizResponseSchema)
async def get_quiz_by_id_full_info(quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_quiz_by_id_full_info(quiz_id, current_user)
    return result


@quiz_router.get("/quizzes/{quiz_id}/questions", response_model=QuestionListSchema)
async def get_quiz_questions(quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_quiz_questions_to_response(quiz_id, current_user)
    return result


@quiz_router.get("/questions/{question_id}/answers", response_model=AnswerListSchema)
async def get_question_answers(question_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_question_answers_to_response(question_id, current_user)
    return result


@quiz_router.delete("/quizzes/{quiz_id}/delete/")
async def delete_quiz(quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)) -> str:
    service = QuizService(db)
    result = await service.delete_quiz(quiz_id, current_user)
    return result


@quiz_router.patch("/quizzes/{quiz_id}/update/", response_model=QuizResponseSchema)
async def update_quiz(quiz_data: QuizUpdateSchema, quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.update_quiz(quiz_data, quiz_id, current_user)
    return result


@quiz_router.get("/quizzes/{company_id}/list-quizzes", response_model=QuizListSchema)
async def list_quizzes(company_id: UUID, page: int = 1, limit: int = 5, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.list_quizzes(company_id, current_user, page, limit)
    return result

# be-12


@quiz_router.post("/company/{company_id}/quizzes/{quiz_id}/start")
async def start_quiz(user_answers: AnswerQuestionListSchema, company_id: UUID, quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.submit_quiz_answers(user_answers, company_id, quiz_id, current_user)
    return result


@quiz_router.get("/company/{company_id}/quizzes/{quiz_id}/results")
async def get_quiz_results(company_id: UUID, quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_quiz_results(company_id, quiz_id, current_user)
    return result

# get all quizzes avarage mark


@quiz_router.get("/company/{user_id}/avarage-mark-from-quizzes")
async def get_user_avarage_mark_from_quizzes(user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_user_avarage_mark_from_quizzes(user_id, current_user)
    return result

# get all quizzes user avarage mark in company


@quiz_router.get("/company/{company_id}/user/{user_id}/avarage-mark-from-quizzes")
async def get_user_avarage_mark_from_quizzes_in_company(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_user_avarage_mark_from_quizzes_in_company(user_id, company_id, current_user)
    return result


@quiz_router.get("/get-saved-results-redis/{key}")
async def get_saved_results_redis(key: str, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_data_from_redis(key)
    return result

# be-14


@quiz_router.get("/get-results-of-user-in-company/{company_id}/{user_id}")
async def get_results_of_user_in_company(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_results_of_user_in_company(user_id, company_id, current_user)
    return result


@quiz_router.get("/get-results-of-all_users-in-company/{company_id}")
async def get_results_of_all_users_in_company(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_results_of_all_users_in_company(company_id, current_user)
    return result

