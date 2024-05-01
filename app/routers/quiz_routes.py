from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connect_postgresql import get_session
from fastapi import APIRouter, HTTPException, status

from app.db.user_models import User, Company
from app.schemas.quiz_shemas import QuizCreateSchema, QuizUpdateSchema
from app.services.quiz_service import QuizService
from app.services.user_service import get_current_user_from_token
from uuid import UUID

quiz_router = APIRouter(tags=["Quizzes"])


@quiz_router.post("/quizzes/{company_id}/create")
async def create_quiz(company_id: UUID, quiz_data: QuizCreateSchema, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.create_quiz(quiz_data, current_user, company_id)
    return result


@quiz_router.get("/quizzes/{quiz_id}")
async def get_quiz_by_id(quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_quiz_by_id(quiz_id, current_user)
    return result


@quiz_router.get("/quizzes/{quiz_id}/full")
async def get_quiz_by_id_full_info(quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_quiz_by_id_full_info(quiz_id, current_user)
    return result


@quiz_router.get("/quizzes/{quiz_id}/questions")
async def get_quiz_questions(quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_quiz_questions_to_response(quiz_id, current_user)
    return result


@quiz_router.get("/questions/{question_id}/answers")
async def get_question_answers(question_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.get_question_answers_to_response(question_id, current_user)
    return result


@quiz_router.delete("/quizzes/{company_id}/delete/{quiz_id}")
async def delete_quiz(company_id: UUID, quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.delete_quiz(quiz_id, current_user, company_id)
    return result


@quiz_router.patch("/quizzes/{company_id}/update/{quiz_id}")
async def update_quiz(quiz_data: QuizUpdateSchema, company_id: UUID, quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.update_quiz(quiz_data, company_id, quiz_id, current_user)
    return result


@quiz_router.get("/quizzes/{company_id}/list-quizzes")
async def list_quizzes(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    result = await service.list_quizzes(company_id, current_user)
    return result
