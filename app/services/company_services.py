from typing import List, Optional
from app.repositories.company_repository import CompanyRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.company_schemas import CompanyCreateSchema, CompanyDetailSchema, CompanyListSchema
import bcrypt
import logging
from fastapi import HTTPException
from app.db.company_models import Company
from uuid import UUID
from app.auth.jwtauth import oauth2_scheme
from jose import jwt
from fastapi import Depends
from app.db.connect_postgresql import get_session
from app.db.user_models import User


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.company_repository = CompanyRepository(db)

    async def create_company(self, company_data: CompanyCreateSchema, current_user: User) -> Company:
        current_user_id = current_user.id
        company = await self.company_repository.create_company(company_data.dict(), current_user_id)
        return company

    async def get_company_by_id(self, company_id: UUID) -> CompanyDetailSchema:
        company = await self.company_repository.get_company_by_id(company_id)
        return company

    async def get_companies_list_paginated(self, page: int, limit: int) -> List[CompanyDetailSchema]:
        companies = await self.company_repository.get_company_list_paginated(page, limit)
        return CompanyListSchema(companies=[CompanyDetailSchema.from_orm(company) for company in companies])

    async def delete_company(self, company_id: UUID, current_user: User):
        await self.check_if_owner_of_company(company_id, current_user)
        await self.company_repository.delete_company(company_id)
        return {"message": "Company deleted successfully"}

    async def update_company(self, company_id: UUID, company_data: dict, current_user: User) -> CompanyDetailSchema:
        await self.check_if_owner_of_company(company_id, current_user)
        company = await self.company_repository.update_company(company_id, company_data)
        return company

    async def check_if_owner_of_company(self, company_id: UUID, current_user: User):
        company = await self.company_repository.get_company_without_visability(company_id)
        if company.owner_id != current_user.id:
            raise HTTPException(
                status_code=401, detail="You are not authorized to update/delete this company")
