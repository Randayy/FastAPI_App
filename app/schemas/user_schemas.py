from pydantic import BaseModel , validator
from typing import List, Optional
from pydantic.fields import Field
from uuid import UUID


class UserSchema(BaseModel):
    username: str = Field(..., min_length=6, description="Username must be at least 6 characters long")
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class SignUpRequestSchema(UserSchema):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    confirm_password: Optional[str] = Field(None, min_length=8, description="Password must be at least 8 characters long")

class SignInRequestSchema(BaseModel):
    username: str = Field(..., min_length=6, description="Username must be at least 6 characters long")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class UserUpdateRequestSchema(UserSchema):
    current_password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

class UserDetailSchema(UserSchema):
    id: UUID
    class Config:
        orm_mode = True

class UserListSchema(BaseModel):
    users: List[UserDetailSchema]
    class Config:
        orm_mode = True