from typing import List, Optional
from app.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schemas import SignUpRequestSchema, UserDetailSchema, UserUpdateRequestSchema, UserListSchema, UserInvitationSchema, UserInvitationListSchema, UserRequestSchema, UserInvitationListSchema
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
from fastapi import status


settings = Settings()


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)) -> UserDetailSchema:
    try:
        payload = jwt.decode(token.credentials, settings.auth0_secret_key,
                             algorithms=[settings.jwt_algorithm], audience=settings.auth0_audience, issuer=settings.auth0_issuer)
        username: str = payload.get("sub")
        email: str = payload.get("email")
        exp: int = payload.get("exp")
        if not username:
            raise HTTPException(
                status_code=401, detail="No Username found in token")
        if not email:
            raise HTTPException(
                status_code=401, detail="No Email found in token")

        token_data = TokenData(sub=username, exp=exp, email=email)
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Token has expired")
    old_user = await UserRepository(db).get_user_by_email(email=token_data.email)
    if not old_user:
        user_creation = await UserService(db).create_user_from_token(email=token_data.email)
        return user_creation
    else:
        exp_date = datetime.fromtimestamp(token_data.exp)
        current_date = datetime.now()
        if current_date > exp_date:
            raise HTTPException(
                status_code=401, detail="Token has expired")
        return old_user


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

    async def get_user_by_id(self, user_id: UUID, current_user: User) -> UserDetailSchema:
        user = await self.user_repository.get_user_by_id(user_id)
        current_user_id = current_user.id
        await self.check_user_permissions(user_id, current_user_id)
        return user

    async def get_users_list(self) -> List[UserDetailSchema]:
        users = await self.user_repository.get_users_list()
        return users

    async def get_users_list_paginated(self, page: int, limit: int) -> List[UserDetailSchema]:
        users = await self.user_repository.get_users_list_paginated(page, limit)
        return UserListSchema(users=[UserDetailSchema.from_orm(user) for user in users])

    async def delete_user(self, user_id: UUID, current_user: User) -> None:
        await self.check_user_permissions(user_id, current_user.id)
        await self.user_repository.delete_user(user_id)

    async def update_user(self, user_id: UUID, user_data: UserUpdateRequestSchema, current_user: User) -> UserDetailSchema:
        await self.check_user_permissions(user_id, current_user.id)
        user = await self.user_repository.get_user_by_id(user_id)

        current_password = user.password
        entered_password = user_data['current_password']

        check_username_exists = await self.user_repository.get_user_by_username(user_data['username'])
        if check_username_exists:
            raise HTTPException(
                status_code=400, detail="user with username already exists")

        check = await verify_password(entered_password, current_password)
        if not check:
            raise HTTPException(
                status_code=400, detail="incorrect password")

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

    async def create_user_from_token(self, email: str) -> UserDetailSchema:
        password_pref = 'auth0' + email.split("@")[0]
        password = password_pref + "test"
        new_user_data = {
            "username": email.split("@")[0],
            "email": email,
            "password": password,
            "confirm_password": password,
            "first_name": email.split("@")[0],
            "last_name": "yourlatname",
        }
        check_user_by_username = await self.get_user_by_username(new_user_data["username"])
        if not check_user_by_username:
            created_user = await self.create_user(SignUpRequestSchema(**new_user_data))
        else:
            new_user_data["username"] = new_user_data["username"] + "auth0"
            created_user = await self.create_user(SignUpRequestSchema(**new_user_data))
        return created_user

    async def check_user_permissions(self, user_id: UUID, current_user_id: UUID) -> bool:
        if current_user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You dont have permission to access this user")

    async def get_my_invitations(self, current_user: User) -> List[UserInvitationSchema]:
        user_invitations = await self.user_repository.get_my_invitations(current_user.id)
        return UserInvitationListSchema(invitations=[UserInvitationSchema.from_orm(invitation) for invitation in user_invitations])

    async def get_my_requests(self, current_user: User) -> List[UserRequestSchema]:
        user_requests = await self.user_repository.get_my_requests(current_user.id)
        return UserInvitationListSchema(invitations=[UserInvitationSchema.from_orm(request) for request in user_requests])
