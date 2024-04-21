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


SECRET_KEY = 'FE3FDF34FE3FF34F34F34F34F'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JWTAuth():
    def __init__(self, db: AsyncSession):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.user_repository = UserRepository(db)

    async def authenticate_user(self, username: str, password: str):
        user = await self.user_repository.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        current_password = user.password
        if not verify_password(password, current_password):
            raise HTTPException(status_code=400, detail="Incorrect password")
        return user

    async def create_access_token(self, data: dict):
        to_encode = data.copy()
        if self.access_token_expire_minutes:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
        except jwt.JWTError:
            raise HTTPException(
                status_code=403, detail="Could not validate credentials")
        return await self.user_repository.get_user_by_username(username)
