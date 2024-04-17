from pydantic import BaseModel
from typing import List, Optional
from pydantic.fields import Field


class UserSchema(BaseModel):
    username: str = Field(..., min_length=6)
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class SignUpRequestSchema(UserSchema):
    password: str = Field(..., min_length=8)


class SignInRequestSchema(BaseModel):
    username: str
    password: str


class UserUpdateRequestSchema(UserSchema):
    current_password: str
    new_password: str

class UserDetailSchema(UserSchema):
    id: int
    class Config:
        orm_mode = True

class UserListSchema(BaseModel):
    users: List[UserDetailSchema]
    class Config:
        orm_mode = True