from pydantic import BaseModel, validator
from typing import List, Optional
from pydantic.fields import Field
from uuid import UUID


class CompanySchema(BaseModel):
    name: str
    description: Optional[str] = None
    visible: bool

    class Config:
        from_attributes = True


class CompanyBaseSchema(BaseModel):
    name: str
    description: Optional[str] = None
    visible: bool

    class Config:
        from_attributes = True


class CompanyCreateSchema(CompanyBaseSchema):

    class Config:
        from_attributes = True


class CompanyDetailSchema(CompanySchema):
    id: UUID

    class Config:
        from_attributes = True


class CompanyListSchema(BaseModel):
    companies: List[CompanyDetailSchema]

    class Config:
        from_attributes = True


class CompanyUpdateSchema(CompanyBaseSchema):
    class Config:
        from_attributes = True


class CompanyActionSchema(BaseModel):
    message: Optional[str] = None
    user_id: UUID
    company_id: UUID

    class Config:
        from_attributes = True
