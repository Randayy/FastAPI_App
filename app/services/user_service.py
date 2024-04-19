from typing import List, Optional
from app.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schemas import SignUpRequestSchema, UserDetailSchema, UserUpdateRequestSchema,UserListSchema
import bcrypt
import logging
from fastapi import HTTPException
from app.db.user_models import User
from uuid import UUID


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)

    async def create_user(self, user_data: SignUpRequestSchema) -> User:
        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        hashed_password = await self.hash_password(user_data.password)
        user_data_dict = user_data.dict()
        user_data_dict.pop('confirm_password', None)
        user_data_dict['password'] = hashed_password
        user = await self.user_repository.create_user(user_data_dict)
        return user

    async def get_user_by_id(self, user_id: UUID) -> UserDetailSchema:
        user = await self.user_repository.get_user_by_id(user_id)
        return user

    async def get_users_list(self) -> List[UserDetailSchema]:
        users = await self.user_repository.get_users_list()
        return users

    async def get_users_list_paginated(self, page: int, limit: int) -> List[UserDetailSchema]:
        users = await self.user_repository.get_users_list_paginated(page, limit)
        return UserListSchema(users=[UserDetailSchema.from_orm(user) for user in users])

    async def delete_user(self, user_id: UUID) -> None:
        await self.user_repository.delete_user(user_id)
        return None

    async def update_user(self, user_id: UUID, user_data: UserUpdateRequestSchema) -> UserDetailSchema:
        user = await self.user_repository.get_user_by_id(user_id)
        current_password = user.password
        entered_password = user_data['current_password']

        check_username_exists = await self.user_repository.get_user_by_username(user_data['username'])
        if check_username_exists:
            raise HTTPException(status_code=400, detail="user with username already exists")
        
        check_email_exists = await self.user_repository.get_user_by_email(user_data['email'])
        if check_email_exists:
            raise HTTPException(status_code=400, detail="user with email already exists")


        if not await self.verify_password(entered_password, current_password):
            raise HTTPException(status_code=400, detail="incorrect password")

        updated_user = await self.user_repository.update_user(user, user_data)
        return updated_user

    async def hash_password(self, password: str) -> str:
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
