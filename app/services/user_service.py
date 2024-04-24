from typing import List, Optional
from app.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schemas import SignUpRequestSchema, UserDetailSchema, UserUpdateRequestSchema, UserListSchema
import bcrypt
import logging
from fastapi import HTTPException
from app.db.user_models import User
from uuid import UUID
from app.utils.utils import verify_password, hash_password
from typing import Annotated
from app.auth.jwtauth import oauth2_scheme
from jose import jwt
from fastapi import Depends
from app.db.connect_postgresql import get_session
from app.core.config import Settings
from app.schemas.auth_schemas import TokenData
from jose import JWTError
from datetime import datetime
from app.auth.auth0 import decode_token, http_bearer
from fastapi.security import HTTPAuthorizationCredentials


settings = Settings()


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)

    async def create_user(self, user_data: SignUpRequestSchema) -> User:
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=400, detail="Passwords do not match")
        hashed_password = await hash_password(user_data.password)
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
            raise HTTPException(
                status_code=400, detail="user with username already exists")

        check_email_exists = await self.user_repository.get_user_by_email(user_data['email'])
        if check_email_exists:
            raise HTTPException(
                status_code=400, detail="user with email already exists")

        check = await verify_password(entered_password, current_password)
        if not check:
            raise HTTPException(status_code=400, detail="incorrect password")

        updated_user = await self.user_repository.update_user(user, user_data)
        return updated_user

    async def get_user_by_username(self, username: str) -> User:
        user = await self.user_repository.get_user_by_username(username)
        return user

    async def get_user_by_email(self, email: str) -> User:
        user = await self.user_repository.get_user_by_email(email)
        return user

    async def authenticate_user(self, username: str, password: str) -> UserDetailSchema:
        user = await self.user_repository.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        entered_password = password
        current_password = user.password
        check = await verify_password(entered_password, current_password)
        if not check:
            raise HTTPException(status_code=400, detail="incorrect password")
        return user

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserDetailSchema:
        try:
            payload = jwt.decode(token, settings.secret_key,
                                 algorithms=[settings.jwt_algorithm])
            username: str = payload.get("sub")
            exp: int = payload.get("exp")
            if username is None:
                raise HTTPException(
                    status_code=401, detail="No Username found in token")

            token_data = TokenData(sub=username, exp=exp)
        except JWTError:
            raise HTTPException(
                status_code=401, detail="Token has expired")
        user = await self.user_repository.get_user_by_username(username=token_data.sub)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_current_active_user(self, token: str) -> UserDetailSchema:
        current_user = await self.get_current_user(token)
        return current_user

    async def get_current_user_from_token(self, token: HTTPAuthorizationCredentials) -> UserDetailSchema:
        try:
            current_user = decode_token(token)
        except:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
            )
        current_user_email = current_user.get("email")
        # check if user exists with same email
        # if not create a new user
        check_user_by_email = await self.get_user_by_email(current_user_email)
        if not check_user_by_email:
            new_user_data = {
                "username": current_user.get("email").split("@")[0],
                "email": current_user.get("email"),
                "password": "testpassword",
                "confirm_password": "testpassword",
                "first_name": current_user.get("email").split("@")[0],
                "last_name": "yourlatname",
            }
            # Checking if there already exists a user with the same username
            check_user_by_username = await self.get_user_by_username(new_user_data["username"])
            if not check_user_by_username:
                created_user = await self.create_user(SignUpRequestSchema(**new_user_data))
            else:
                new_user_data["username"] = new_user_data["username"] + "auth0"
                created_user = await self.create_user(SignUpRequestSchema(**new_user_data))
        else:
            found_user = await self.get_user_by_email(current_user_email)
            return found_user

        return created_user
