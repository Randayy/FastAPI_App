from typing import List, Optional
from app.repositories.company_repository import CompanyRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.company_schemas import CompanyCreateSchema, CompanyDetailSchema, CompanyListSchema
import bcrypt
import logging
from fastapi import HTTPException
from app.db.user_models import Company, Role
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

    async def check_if_user_is_member_of_company(self, company_id: UUID, user_id: UUID):
        await self.company_repository.check_if_user_is_member_of_company(company_id, user_id)

    async def check_if_user_is_member_of_company_for_deleting(self, company_id: UUID, user_id: UUID):
        await self.company_repository.check_if_user_is_member_of_company_for_deleting(company_id, user_id)

    async def check_if_owner_not_take_himself(self, current_user: User, user_id: UUID):
        if current_user.id == user_id:
            raise HTTPException(
                status_code=401, detail="Owner cannot invite or delete himself")

    async def check_if_user_invited_already(self, company_id: UUID, user_id: UUID):
        await self.company_repository.check_if_user_invited_already(company_id, user_id)

    async def check_if_user_requested_already(self, company_id: UUID, user_id: UUID):
        await self.company_repository.check_if_user_requested_already(company_id, user_id)

    async def check_if_owner_not_request(self, company_id: UUID, user_id: UUID):
        company = await self.company_repository.get_company_without_visability(company_id)
        if company.owner_id == user_id:
            raise HTTPException(
                status_code=401, detail="Owner cannot send request to join his company")

    async def invite_user_to_company(self, company_id: UUID, user_id: UUID, current_user: User):
        await self.check_if_owner_of_company(company_id, current_user)
        await self.check_if_user_is_member_of_company(company_id, user_id)
        await self.check_if_user_invited_already(company_id, user_id)
        await self.check_if_owner_not_take_himself(current_user, user_id)
        await self.company_repository.invite_user_to_company(company_id, user_id)

    async def cancel_invitation(self, company_id: UUID, user_id: UUID, current_user: User):
        await self.check_if_owner_of_company(company_id, current_user)
        await self.company_repository.cancel_invitation(company_id, user_id)

    async def accept_invitation(self, company_id: UUID, current_user: User):
        user_id = current_user.id
        await self.company_repository.accept_invitation(company_id, user_id)

    async def reject_invitation(self, company_id: UUID, current_user: User):
        await self.company_repository.reject_invitation(company_id, current_user)

    async def delete_user_from_company(self, company_id: UUID, user_id: UUID, current_user: User):
        await self.check_if_owner_of_company(company_id, current_user)
        await self.check_if_user_is_member_of_company_for_deleting(company_id, user_id)
        await self.check_if_owner_not_take_himself(current_user, user_id)
        await self.company_repository.delete_user_from_company(company_id, user_id)

    async def exit_from_company(self, company_id: UUID, current_user: User):
        await self.check_if_user_is_member_of_company_for_deleting(company_id, current_user.id)
        await self.company_repository.exit_from_company(company_id, current_user)

    async def get_invited_users(self, company_id: UUID, current_user: User):
        await self.check_if_owner_of_company(company_id, current_user)
        users = await self.company_repository.get_invited_users(company_id)
        return users

    async def get_requested_users(self, company_id: UUID, current_user: User):
        await self.check_if_owner_of_company(company_id, current_user)
        users = await self.company_repository.get_requested_users(company_id)
        return users

    async def get_company_members(self, company_id: UUID, current_user: User):
        await self.check_if_owner_of_company(company_id, current_user)
        users = await self.company_repository.get_company_members(company_id)
        return users

    async def send_join_request(self, company_id: UUID, current_user: User) -> None:
        await self.check_if_owner_not_request(company_id, current_user.id)
        await self.check_if_user_is_member_of_company(company_id, current_user.id)
        await self.check_if_user_invited_already(company_id, current_user.id)
        await self.check_if_user_requested_already(company_id, current_user.id)
        await self.company_repository.send_join_request(company_id, current_user.id)

    async def cancel_join_request(self, company_id: UUID, current_user: User) -> None:
        await self.company_repository.cancel_join_request(company_id, current_user.id)

    async def accept_join_request(self, company_id: UUID, user_id: UUID, current_user: User) -> None:
        await self.check_if_owner_of_company(company_id, current_user)
        await self.company_repository.accept_join_request(company_id, user_id)

    async def reject_join_request(self, company_id: UUID, user_id: UUID, current_user: User) -> None:
        await self.check_if_owner_of_company(company_id, current_user)
        await self.company_repository.reject_join_request(company_id, user_id)

    # be-10
    async def promote_user_to_admin(self, company_id: UUID, user_id: UUID, current_user: User) -> None:
        await self.check_if_owner_of_company(company_id, current_user)
        role = await self.get_user_role_in_company(company_id, user_id)
        if role != Role.MEMBER:
            raise HTTPException(
                status_code=400, detail="User is already an admin or owner")
        await self.company_repository.promote_user_to_admin(company_id, user_id)

    async def get_user_role_in_company(self, company_id: UUID, user_id: UUID):
        role = await self.company_repository.get_user_role_in_company(company_id, user_id)
        return role
    
    async def demote_admin_to_member(self, company_id: UUID, user_id: UUID, current_user: User) -> None:
        await self.check_if_owner_of_company(company_id, current_user)
        role = await self.get_user_role_in_company(company_id, user_id)
        if role != Role.ADMIN:
            raise HTTPException(
                status_code=400, detail="User is already a member or owner")
        await self.company_repository.demote_admin_to_member(company_id, user_id)

    async def get_company_admins(self, company_id: UUID, current_user: User):
        await self.check_if_owner_of_company(company_id, current_user)
        users = await self.company_repository.get_company_admins(company_id)
        return users
