from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.connect_postgresql import get_session
from app.db.auth_models import Token
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema
from fastapi import APIRouter
from app.services.user_service import UserService
from app.auth.jwtauth import JWTAuth
from uuid import UUID
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.db.user_models import User


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


@user_router.post("/users/token")
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_session)) -> Token:
    auth = JWTAuth(db)
    user = await auth.authenticate_user(form_data.username, form_data.password)
    access_token = await auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
