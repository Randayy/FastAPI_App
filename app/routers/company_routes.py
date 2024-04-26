from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connect_postgresql import get_session
from fastapi import APIRouter, HTTPException, status
from app.db.company_models import Company
from app.db.user_models import User
from app.schemas.company_schemas import CompanyCreateSchema
from app.services.company_services import CompanyService
from app.services.user_service import get_current_user_from_token
from uuid import UUID

company_router = APIRouter(tags=["Company"])

# @company_router.get("/companies")
# # async def get_companies(db: AsyncSession = Depends(get_session)):
# #     companies = await company_service.get_companies_list()
# #     return companies


@company_router.post("/companies")
async def create_company(company_data: CompanyCreateSchema, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    return await service.create_company(company_data, current_user)


@company_router.get("/companies/{company_id}")
async def get_company_by_id(company_id: UUID, db: AsyncSession = Depends(get_session)):
    service = CompanyService(db)
    return await service.get_company_by_id(company_id)


@company_router.get("/companies/")
async def get_companies_list_paginated(page: int = 1, limit: int = 5, db: AsyncSession = Depends(get_session)):
    service = CompanyService(db)
    companies = await service.get_companies_list_paginated(page, limit)
    return companies


@company_router.delete("/companies/{company_id}")
async def delete_company(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.delete_company(company_id, current_user)
    return {"message": "Company deleted successfully"}


@company_router.patch("/companies/{company_id}")
async def update_company(company_id: UUID, company_data: CompanyCreateSchema, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    company = await service.update_company(company_id, company_data.dict(), current_user)
    return company
