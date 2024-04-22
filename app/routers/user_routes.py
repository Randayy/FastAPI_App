from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.connect_postgresql import get_session
from app.schemas.auth_schemas import Token
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema
from fastapi import APIRouter, HTTPException, status
from app.services.user_service import UserService
from app.auth.jwtauth import JWTAuth
from uuid import UUID
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.db.user_models import User
from app.auth.jwtauth import oauth2_scheme

user_router = APIRouter()


@user_router.post("/users", response_model=UserDetailSchema)
async def create_user(user_data: SignUpRequestSchema, db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    return await service.create_user(user_data)


@user_router.get("/users/{user_id}", response_model=UserDetailSchema)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    return await service.get_user_by_id(user_id)


@user_router.get("/users/", response_model=UserListSchema)
async def get_users_list_paginated(page: int = 1, limit: int = 5, db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    users = await service.get_users_list_paginated(page, limit)
    return users


@user_router.delete("/user/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}


@user_router.patch("/user/{user_id}", response_model=UserDetailSchema)
async def update_user(user_id: UUID, user_data: UserUpdateRequestSchema, db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    user = await service.update_user(user_id, user_data.dict())
    return user


@user_router.post("/token")
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_session)) -> Token:
    auth = JWTAuth()
    service = UserService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)
    access_token = await auth.create_access_token({"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@user_router.get("/me", response_model=UserDetailSchema)
async def read_users_me(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    current_user = await service.get_current_active_user(token)
    return current_user
