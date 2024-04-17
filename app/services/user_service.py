from typing import List, Optional
from app.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schemas import SignUpRequestSchema, UserDetailSchema, UserUpdateRequestSchema
import bcrypt
import logging
from fastapi import HTTPException
from uuid import UUID


class UserService:
    def __init__(self, db: AsyncSession):
        self.User_Repository = UserRepository(db)

    async def create_user(self, user_data: SignUpRequestSchema) -> SignUpRequestSchema:
        hashed_password = await self.hash_password(user_data.password)
        user_data_dict = user_data.dict()
        user_data_dict['password'] = hashed_password
        user = await self.User_Repository.create_user(user_data_dict)
        return user

    async def get_user_by_id(self, user_id: UUID) -> UserDetailSchema:
        user = await self.User_Repository.get_user_by_id(user_id)
        return user

    async def get_users_list(self) -> List[UserDetailSchema]:
        users = await self.User_Repository.get_users_list()
        return users

    async def get_users_list_paginated(self, page: int, limit: int) -> List[UserDetailSchema]:
        users = await self.User_Repository.get_users_list_paginated(page, limit)
        return users

    async def delete_user(self, user_id: UUID) -> None:
        await self.User_Repository.delete_user(user_id)
        return None

    async def update_user(self, user_id: UUID, user_data: UserUpdateRequestSchema) -> UserDetailSchema:
        user = await self.User_Repository.get_user_by_id(user_id)
        current_password = user.password
        user_data_entered = user_data
        entered_password = user_data_entered['current_password']

        if not await self.verify_password(entered_password, current_password):
            raise HTTPException(status_code=400, detail="incorrect password")

        updated_user = await self.User_Repository.update_user(user, user_data_entered)
        return updated_user

    async def hash_password(self, password: str) -> str:
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
