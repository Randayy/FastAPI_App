from sqlalchemy import Column, String
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    exp : int | None = None
    sub: str | None = None