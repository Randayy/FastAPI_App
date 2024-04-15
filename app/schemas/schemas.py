from pydantic import BaseModel, EmailStr
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreateSchema(UserBaseSchema):
    password: str

class UserBaseSchema(UserBaseSchema):
    id: int

    class Config:
        orm_mode = True


class SignInRequestSchema(BaseModel):
    username: str
    password: str


class SignUpRequestSchema(UserCreateSchema):
    confirm_password: str


class UserUpdateRequestSchema(UserBaseSchema):
    current_password: str
    new_password: str


class UsersListSchema(BaseModel):
    users: list[UserBaseSchema]


class UserDetailSchema(BaseModel):
    user: UserBaseSchema