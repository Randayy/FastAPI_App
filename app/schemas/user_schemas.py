from pydantic import BaseModel
from typing import List, Optional



class UserSchema(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class SignUpRequestSchema(UserSchema):
    password: str


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