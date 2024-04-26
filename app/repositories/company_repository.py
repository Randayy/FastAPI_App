from app.db.company_models import Company
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException
from sqlalchemy import select
import logging
from sqlalchemy.exc import DBAPIError
from uuid import UUID
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_company(self, company_name: str) -> bool:
        company_check = await self.db.execute(select(Company).where(Company.name == company_name))
        if company_check:
            raise HTTPException(
                status_code=404, detail="Company with name already exists")

    async def create_company(self, company_data: dict, current_user_id: UUID) -> Company:
        await self.check_company(company_data["name"])
        company_data["owner_id"] = current_user_id
        company = Company(**company_data)
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        logging.info("Company created")
        return company

    async def get_company_by_id(self, company_id: UUID) -> Company:
        company = await self.get_company_without_visability(company_id)
        if not company.visible == True:
            raise HTTPException(status_code=404, detail="Company not visible")
        return company

    async def get_company_without_visability(self, company_id: UUID) -> Company:
        company = await self.db.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        logging.info(f"Company found with id {company_id}")
        return company

    async def get_company_list_paginated(self, page: int, limit: int) -> List[Company]:
        companies = await self.db.execute(select(Company).where(Company.visible == True).offset((page - 1) * limit).limit(limit))
        companies = companies.scalars().all()
        if not companies:
            raise HTTPException(
                status_code=404, detail="No companies found or invisible")
        logging.info("Companies found")
        return companies

    async def delete_company(self, company_id: UUID) -> None:
        company = await self.get_company_without_visability(company_id)
        await self.db.delete(company)
        await self.db.commit()
        logging.info(f"Company with id {company_id} deleted")
        return None

    async def update_company(self, company_id: UUID, company_data: dict) -> Company:
        company = await self.get_company_without_visability(company_id)
        for key, value in company_data.items():
            setattr(company, key, value)
        await self.db.commit()
        await self.db.refresh(company)
        return company
