from app.db.user_models import User
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional ,Type
from fastapi import HTTPException
from sqlalchemy import select

class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self,user_data: SignUpRequestSchema) -> SignUpRequestSchema:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        print("Found user:", user)
        return user
    
    async def get_users_list(self) -> List[User]:
        users = await self.db.execute(select(User))
        users = users.scalars().all()

        if not users:
            raise HTTPException(status_code=404, detail="No users found")

        return users
    
    async def delete_user(self, user_id: int) -> None:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        print("Deleting user:", user.username)

        await self.db.delete(user)
        await self.db.commit()
        return None
    

    async def update_user(self, user: User, user_data: dict) -> User:
        for key, value in user_data.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user