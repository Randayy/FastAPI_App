from pydantic import BaseModel, validator
from typing import List, Optional
from pydantic.fields import Field
from uuid import UUID


class UserBaseSchema(BaseModel):
    username: Optional[str] = Field(..., min_length=6,
                                    description="Username must be at least 6 characters long")
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserSchema(UserBaseSchema):
    email: str


class UserBaseSchema(BaseModel):
    username: Optional[str] = Field(..., min_length=6,
                                    description="Username must be at least 6 characters long")
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class SignUpRequestSchema(UserSchema):
    password: str = Field(..., min_length=8,
                          description="Password must be at least 8 characters long")
    confirm_password: Optional[str] = Field(
        None, min_length=8, description="Password must be at least 8 characters long")

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError("Passwords do not match")
        return v


class SignInRequestSchema(BaseModel):
    username: str = Field(..., min_length=6,
                          description="Username must be at least 6 characters long")
    password: str = Field(..., min_length=8,
                          description="Password must be at least 8 characters long")


class UserUpdateRequestSchema(UserBaseSchema):
    current_password: str = Field(..., min_length=8,
                                  description="Password must be at least 8 characters long")
    new_password: str = Field(..., min_length=8,
                              description="Password must be at least 8 characters long")


class UserDetailSchema(UserSchema):
    id: UUID

    class Config:
        from_attributes = True


class UserListSchema(BaseModel):
    users: List[UserDetailSchema]

    class Config:
        from_attributes = True
