from pydantic import BaseModel, EmailStr
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class SignInRequestSchema(BaseModel):
    username: str
    password: str


class SignUpRequestSchema(UserCreate):
    confirm_password: str


class UserUpdateRequestSchema(UserBase):
    current_password: str
    new_password: str


class UsersListSchema(BaseModel):
    users: list[User]


class UserDetailSchema(BaseModel):
    user: User