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


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class SignInRequestModel(BaseModel):
    username: str
    password: str


class SignUpRequestModel(UserCreate):
    confirm_password: str


class UserUpdateRequestModel(UserUpdate):
    current_password: str
    new_password: str


class UsersListResponse(BaseModel):
    users: list[User]


class UserDetailResponse(BaseModel):
    user: User