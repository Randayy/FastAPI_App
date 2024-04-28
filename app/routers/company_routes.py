from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connect_postgresql import get_session
from fastapi import APIRouter, HTTPException, status

from app.db.user_models import User ,Company
from app.schemas.company_schemas import CompanyCreateSchema
from app.services.company_services import CompanyService
from app.services.user_service import get_current_user_from_token
from uuid import UUID

company_router = APIRouter(tags=["Company"])


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

@company_router.post("/companies/{company_id}/invite{user_id}")
async def invite_user_to_company(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.invite_user_to_company(company_id, user_id, current_user)
    return {"message": "User invited successfully"}

@company_router.post("/companies/{company_id}/accept")
async def accept_invitation(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.accept_invitation(company_id, current_user)
    return {"message": "Invitation accepted successfully"}

@company_router.post("/companies/{company_id}/reject")
async def reject_invitation(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.reject_invitation(company_id, current_user)
    return {"message": "Invitation rejected successfully"}

@company_router.delete("/companies/{company_id}/cancel_invitation/{user_id}")
async def cancel_invitation(company_id: UUID,user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.cancel_invitation(company_id,user_id, current_user)
    return {"message": "Invitation cancelled successfully"}

@company_router.delete("/companies/{company_id}/delete/{user_id}")
async def delete_user_from_company(company_id,user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.delete_user_from_company(company_id,user_id, current_user)
    return {"message": "User deleted from company successfully"}

@company_router.post("/companies/{company_id}/exit")
async def exit_from_company(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.exit_from_company(company_id, current_user)
    return {"message": "User exited from company successfully"}

@company_router.get("/companies/{company_id}/invited_users")
async def get_invited_users(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    return await service.get_invited_users(company_id, current_user)

@company_router.get("/companies/{company_id}/requested_users")
async def get_requested_users(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    return await service.get_requested_users(company_id, current_user)

@company_router.get("/companies/{company_id}/members")
async def get_company_members(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    return await service.get_company_members(company_id,current_user)


@company_router.post("/send_join_request/{company_id}")
async def send_join_request(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.send_join_request(company_id, current_user)
    return {"message": "Join request sent successfully"}

@company_router.delete("/cancel_join_request/{company_id}")
async def cancel_join_request(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.cancel_join_request(company_id, current_user)
    return {"message": "Join request cancelled successfully"}

@company_router.post("/accept_join_request/{company_id}/{user_id}")
async def accept_join_request(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.accept_join_request(company_id, user_id, current_user)
    return {"message": "Join request accepted successfully"}

@company_router.post("/reject_join_request/{company_id}/{user_id}")
async def reject_join_request(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.reject_join_request(company_id, user_id, current_user)
    return {"message": "Join request rejected successfully"}

