from app.db.user_models import User
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException
from sqlalchemy import select
import logging
from sqlalchemy.exc import DBAPIError
from uuid import UUID


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logging.info("User created")
        return user

    async def get_user_by_id(self, user_id: UUID) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        logging.info(f"User found with id {user_id}")
        return user

    async def get_users_list(self) -> List[User]:
        users = await self.db.execute(select(User))
        users = users.scalars().all()
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        logging.info("Users found")
        return users

    async def get_users_list_paginated(self, page: int, limit: int) -> List[User]:
        users = await self.db.execute(select(User).offset((page - 1) * limit).limit(limit))
        users = users.scalars().all()
        if not users and users != []:
            raise HTTPException(
                status_code=404, detail=f"No users found at page {page}")
        logging.info(f"Users found at page {page}")
        return users

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        print("Deleting user:", user.username)
        await self.db.delete(user)
        await self.db.commit()
        logging.info(f"User with id {user_id} deleted")
        return None

    async def update_user(self, user: User, user_data: dict) -> User:
        for key, value in user_data.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        logging.info(f"User with id {user.id} updated")
        return user
    
    async def get_user_by_username(self, username: str) -> User:
        user = await self.db.execute(select(User).where(User.username == username))
        user = user.scalars().first()
        if user:
            return True
        return False
        
    async def get_user_by_email(self, email: str) -> User:
        user = await self.db.execute(select(User).where(User.email == email))
        user = user.scalars().first()
        if user:
            return True
        return False
