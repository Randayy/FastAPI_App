from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connect_postgresql import get_session
from fastapi import APIRouter, HTTPException, status

from app.db.user_models import User, Company
from app.schemas.company_schemas import CompanyCreateSchema, CompanyActionSchema
from app.services.company_services import CompanyService
from app.services.quiz_service import QuizService
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


@company_router.post("/companies/{company_id}/invite{user_id}", response_model=CompanyActionSchema)
async def invite_user_to_company(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.invite_user_to_company(company_id, user_id, current_user)
    return CompanyActionSchema(message="Invitation sent successfully!", company_id=company_id, user_id=user_id)


@company_router.post("/companies/{company_id}/accept", response_model=CompanyActionSchema)
async def accept_invitation(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    user_id = current_user.id
    await service.accept_invitation(company_id, current_user)
    return CompanyActionSchema(message="Invitation accepted successfully!", company_id=company_id, user_id=user_id)


@company_router.post("/companies/{company_id}/reject", response_model=CompanyActionSchema)
async def reject_invitation(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    user_id = current_user.id
    await service.reject_invitation(company_id, current_user)
    return CompanyActionSchema(message="Invitation rejected successfully!", company_id=company_id, user_id=user_id)


@company_router.delete("/companies/{company_id}/cancel_invitation/{user_id}", response_model=CompanyActionSchema)
async def cancel_invitation(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.cancel_invitation(company_id, user_id, current_user)
    return CompanyActionSchema(message="Invitation cancelled successfully!", company_id=company_id, user_id=user_id)


@company_router.delete("/companies/{company_id}/delete/{user_id}")
async def delete_user_from_company(company_id, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.delete_user_from_company(company_id, user_id, current_user)
    return CompanyActionSchema(message="User deleted successfully!", company_id=company_id, user_id=user_id)


@company_router.post("/companies/{company_id}/exit", response_model=CompanyActionSchema)
async def exit_from_company(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    user_id = current_user.id
    await service.exit_from_company(company_id, current_user)
    return CompanyActionSchema(message="Exited from company successfully!", company_id=company_id, user_id=user_id)


@company_router.get("/companies/{company_id}/invited-users")
async def get_invited_users(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    return await service.get_invited_users(company_id, current_user)


@company_router.get("/companies/{company_id}/requested-users")
async def get_requested_users(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    return await service.get_requested_users(company_id, current_user)


@company_router.get("/companies/{company_id}/members")
async def get_company_members(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    return await service.get_company_members(company_id, current_user)


@company_router.post("/send-join-request/{company_id}", response_model=CompanyActionSchema)
async def send_join_request(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    user_id = current_user.id
    await service.send_join_request(company_id, current_user)
    return CompanyActionSchema(message="Join request sent successfully!", company_id=company_id, user_id=user_id)


@company_router.delete("/cancel-join-request/{company_id}", response_model=CompanyActionSchema)
async def cancel_join_request(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    user_id = current_user.id
    await service.cancel_join_request(company_id, current_user)
    return CompanyActionSchema(message="Join request cancelled successfully!", company_id=company_id, user_id=user_id)


@company_router.post("/accept-join-request/{company_id}/{user_id}", response_model=CompanyActionSchema)
async def accept_join_request(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.accept_join_request(company_id, user_id, current_user)
    return CompanyActionSchema(message="Join request accepted successfully!", company_id=company_id, user_id=user_id)


@company_router.post("/reject-join-request/{company_id}/{user_id}", response_model=CompanyActionSchema)
async def reject_join_request(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.reject_join_request(company_id, user_id, current_user)
    return CompanyActionSchema(message="Join request rejected successfully!", company_id=company_id, user_id=user_id)

# BE-10


@company_router.get("/companies/{company_id}/promote-user-to-admin{user_id}")
async def promote_user_to_admin(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.promote_user_to_admin(company_id, user_id, current_user)
    return CompanyActionSchema(message="User promoted to admin successfully!", company_id=company_id, user_id=user_id)


@company_router.get("/companies/{company_id}/demote-admin-to-user{user_id}")
async def demote_admin_to_user(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    await service.demote_admin_to_member(company_id, user_id, current_user)
    return CompanyActionSchema(message="Admin demoted to user successfully!", company_id=company_id, user_id=user_id)


@company_router.get("/companies/{company_id}/admins")
async def get_company_admins(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = CompanyService(db)
    return await service.get_company_admins(company_id, current_user)

# 15


@company_router.get("/companies/get-avarage-marks-all-members/{company_id}")
async def get_avarage_marks_all_members(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    return await service.get_avarage_marks_all_members(current_user, company_id)


@company_router.get("/companies/{company_id}/get-avarage-marks-of-user/{user_id}")
async def get_avarage_marks_of_user(company_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    return await service.get_avarage_marks_of_member(current_user, company_id, user_id)


@company_router.get("/companies/{company_id}/get-members-and-last-quiz-submition")
async def get_members_and_last_quiz_submition(company_id: UUID, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user_from_token)):
    service = QuizService(db)
    return await service.get_members_and_last_quiz_submition(current_user, company_id)
