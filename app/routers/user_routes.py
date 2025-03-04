from app.services.user_service import get_current_user_from_token
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.connect_postgresql import get_session
from app.schemas.auth_schemas import Token
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema, UserInvitationListSchema
from fastapi import APIRouter, HTTPException, status
from app.services.user_service import UserService
from app.services.quiz_service import QuizService
from app.auth.jwtauth import JWTAuth
from uuid import UUID
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.db.user_models import User
from app.auth.jwtauth import oauth2_scheme
from fastapi.security import HTTPAuthorizationCredentials
from app.services.user_service import get_current_user_from_token


user_router = APIRouter()


@user_router.post("/users", response_model=UserDetailSchema)
async def create_user(user_data: SignUpRequestSchema, db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    return await service.create_user(user_data)


@user_router.get("/users/{user_id}", response_model=UserDetailSchema)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = UserService(db)
    return await service.get_user_by_id(user_id, current_user)


@user_router.get("/users/", response_model=UserListSchema)
async def get_users_list_paginated(page: int = 1, limit: int = 5, db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    users = await service.get_users_list_paginated(page, limit)
    return users


@user_router.delete("/user/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = UserService(db)
    await service.delete_user(user_id, current_user)
    return {"message": "User deleted successfully"}


@user_router.patch("/user/{user_id}", response_model=UserDetailSchema)
async def update_user(user_id: UUID, user_data: UserUpdateRequestSchema, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = UserService(db)
    user = await service.update_user(user_id, user_data.dict(), current_user)
    return user


@user_router.post("/token")
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_session)) -> Token:
    auth = JWTAuth()
    service = UserService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)
    access_token = await auth.create_access_token({"sub": user.username, "email": user.email})
    return Token(access_token=access_token, token_type="bearer")


@user_router.get("/me", response_model=UserDetailSchema)
async def read_users_me(db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    return UserDetailSchema(**current_user.__dict__)


@user_router.get("/my-invitations", response_model=UserInvitationListSchema)
async def get_my_invitations(db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = UserService(db)
    invitations = await service.get_my_invitations(current_user)
    return invitations


@user_router.post("/my-requests")
async def get_my_requests(db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = UserService(db)
    requests = await service.get_my_requests(current_user)
    return requests


# be-14
# it is number of user_answer in redis (special id if user need to get only answers with this id)
@user_router.post("/get-my-quiz-results/{quiz_id}/{redis_id}")
async def get_my_quiz_results(quiz_id: UUID, redis_id: int, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    current_user_id = current_user.id
    key = f"user_answer:{current_user_id}:{quiz_id}:{redis_id}"
    results = await service.get_data_from_redis(key)
    return results


@user_router.post("/get-my-quiz-results/{quiz_id}")
async def get_my_quiz_results(quiz_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    current_user_id = current_user.id
    results = await service.get_all_user_answer_records(current_user_id, quiz_id)
    return results
# be-15


@user_router.post("/get-my-rating")
async def get_my_rating(db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    current_user_id = current_user.id
    rating = await service.get_user_rating(current_user_id)
    return rating


@user_router.post("/get-my-list-of-avarage-marks")
async def get_my_list_of_avarage_marks(db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    current_user_id = current_user.id
    rating = await service.get_average_scores(current_user_id)
    return rating


@user_router.post("/get-my-submited-quizzes")
async def get_my_submited_quizzes(db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    current_user_id = current_user.id
    list_quizzes = await service.get_list_of_quizzes_which_i_submit(current_user_id)
    return list_quizzes
