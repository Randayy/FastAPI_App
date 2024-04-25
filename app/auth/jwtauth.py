from app.utils.utils import verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from fastapi import Depends
from fastapi import HTTPException
from typing import Annotated
from app.core.config import Settings
from app.schemas.auth_schemas import Token
import logging

settings = Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = HTTPBearer()


class JWTAuth():
    def __init__(self):
        self.audience = settings.auth0_audience
        self.issuer = settings.auth0_issuer
        self.secret_key = settings.auth0_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes

    async def create_access_token(self, data: dict) -> Token:
        to_encode = data.copy()
        if self.access_token_expire_minutes:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        to_encode.update({"iss": self.issuer})
        to_encode.update({"aud": self.audience})
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
