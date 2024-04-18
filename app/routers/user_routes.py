from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.connect_postgresql import get_session
from app.db.user_models import User
from sqlalchemy import select
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema
from sqlalchemy.sql import text
from fastapi import HTTPException
from fastapi import APIRouter
from app.services.user_service import UserService
from uuid import UUID


user_router = APIRouter()


@user_router.post("/user", response_model=UserDetailSchema)
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
    return {"users": users}


@user_router.delete("/user/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}


@user_router.put("/user/{user_id}", response_model=UserDetailSchema)
async def update_user(user_id: UUID, user_data: UserUpdateRequestSchema, db: AsyncSession = Depends(get_session)):
    service = UserService(db)
    user = await service.update_user(user_id, user_data.dict())
    return user
