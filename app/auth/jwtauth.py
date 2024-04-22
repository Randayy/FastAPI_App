from app.utils.utils import verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from fastapi import HTTPException
from typing import Annotated
from app.core.config import Settings
from app.schemas.auth_schemas import TokenData
import logging

settings = Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JWTAuth():
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes

    async def create_access_token(self, data: dict) -> TokenData:
        to_encode = data.copy()
        if self.access_token_expire_minutes:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
