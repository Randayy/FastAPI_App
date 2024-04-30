from app.db.user_models import Company
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from app.db.user_models import User, Role
import logging
from sqlalchemy.exc import DBAPIError
from uuid import UUID
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError
from app.db.user_models import Action, ActionStatus, CompanyMember
from sqlalchemy.sql import text
from sqlalchemy import delete


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_company(self, company_name: str) -> bool:
        company_check = await self.db.execute(select(Company).where(Company.name == company_name))
        company_check = company_check.scalars().first()
        if company_check:
            raise HTTPException(
                status_code=404, detail=f"Company with name already exists")

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
        

    async def update_company(self, company_id: UUID, company_data: dict) -> Company:
        company = await self.get_company_without_visability(company_id)
        for key, value in company_data.items():
            setattr(company, key, value)
        await self.db.commit()
        await self.db.refresh(company)
        return company

    async def invite_user_to_company(self, company_id: UUID, user_id: UUID) -> None:
        company = await self.get_company_without_visability(company_id)
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        company_id = company.id
        user_id = user.id
        invitation_creation = Action(
            company_id=company_id, user_id=user_id, status=ActionStatus.INVITED)
        self.db.add(invitation_creation)
        await self.db.commit()
        await self.db.refresh(invitation_creation)
        logging.info("User invited to company")


    async def get_request(self, company_id: UUID, user_id: UUID):
        request = await self.db.execute(select(Action).where(Action.company_id == company_id).where(Action.user_id == user_id).where(Action.status == ActionStatus.REQUESTED))
        request = request.scalars().first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        return request

    async def get_invitation(self, company_id: UUID, current_user_id: UUID):
        invitation = await self.db.execute(select(Action).where(Action.company_id == company_id).where(Action.user_id == current_user_id).where(Action.status == ActionStatus.INVITED))
        invitation = invitation.scalars().first()
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found")
        return invitation

    async def get_invitation_for_deleting(self, company_id: UUID, current_user_id: UUID):
        invitation = await self.db.execute(select(Action).where(Action.company_id == company_id).where(Action.user_id == current_user_id).where(Action.status == ActionStatus.ACCEPTED))
        invitation = invitation.scalars().first()
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found")
        return invitation

    async def cancel_invitation(self, company_id: UUID, user_id: UUID) -> None:
        action = await self.get_invitation(company_id, user_id)
        if action.status == ActionStatus.INVITED:
            action.status = ActionStatus.CANCELLED
            self.db.add(action)
            await self.db.commit()
            await self.db.refresh(action)
            logging.info("Invitation cancelled")

    async def cancel_invitation_delete(self, company_id: UUID, user_id: UUID) -> None:
        action = await self.get_invitation_for_deleting(company_id, user_id)
        if action.status == ActionStatus.ACCEPTED:
            action.status = ActionStatus.CANCELLED
            await self.db.commit()
            logging.info("Invitation cancelled")

    async def check_if_user_is_member_of_company_for_deleting(self, company_id: UUID, user_id: UUID) -> None:
        company_member = await self.db.execute(select(CompanyMember).where(CompanyMember.company_id == company_id).where(CompanyMember.user_id == user_id))
        company_member = company_member.scalars().first()
        return company_member

    async def check_if_user_is_member_of_company(self, company_id: UUID, user_id: UUID) -> None:
        company_member = await self.check_if_user_is_member_of_company_for_deleting(company_id, user_id)
        if company_member:
            raise HTTPException(
                status_code=409, detail="User already member of company")

    async def check_if_user_invited_already(self, company_id: UUID, user_id: UUID) -> None:
        invitation = await self.db.execute(select(Action).where(Action.company_id == company_id).where(Action.user_id == user_id).where(Action.status == ActionStatus.INVITED))
        invitation = invitation.scalars().first()
        if invitation:
            raise HTTPException(status_code=409, detail="User already invited")

    async def check_if_user_requested_already(self, company_id: UUID, user_id: UUID) -> None:
        action = await self.db.execute(select(Action).where(Action.company_id == company_id).where(Action.user_id == user_id).where(Action.status == ActionStatus.REQUESTED))
        action = action.scalars().first()
        if action:
            if action.status == ActionStatus.REQUESTED:
                raise HTTPException(
                    status_code=409, detail="User already requested")

    async def accept_join_request(self, company_id: UUID, user_id: UUID) -> None:
        action = await self.get_request(company_id, user_id)
        if action.status == ActionStatus.REQUESTED:
            action.status = ActionStatus.ACCEPTED
            company_member_adding = CompanyMember(
                company_id=company_id, user_id=user_id, role=Role.MEMBER)
            self.db.add(company_member_adding)
            await self.db.commit()
            await self.db.refresh(company_member_adding)
            logging.info("Join request accepted")
        else:
            raise HTTPException(
                status_code=409, detail="Request already accepted")

    async def accept_invitation(self, company_id: UUID, user_id: UUID) -> None:
        action = await self.get_invitation(company_id, user_id)
        if action.status == ActionStatus.INVITED:
            action.status = ActionStatus.ACCEPTED
            company_member_adding = CompanyMember(
                company_id=company_id, user_id=user_id, role=Role.MEMBER)
            self.db.add(action)
            self.db.add(company_member_adding)
            await self.db.commit()
            await self.db.refresh(company_member_adding)
            await self.db.refresh(action)
            logging.info("Invitation accepted")
        else:
            raise HTTPException(
                status_code=409, detail="Invite already accepted")

    async def delete_user_from_company(self, company_id: UUID, user_id: UUID) -> None:
        company_member = await self.get_member(company_id, user_id)
        await self.db.execute(delete(CompanyMember).where(CompanyMember.company_id == company_id).where(CompanyMember.user_id == user_id))
        await self.db.commit()
        await self.cancel_invitation_delete(company_id, user_id)
        logging.info("User deleted from company")

    async def reject_invitation(self, company_id: UUID, current_user: User) -> None:
        action = await self.get_invitation(company_id, current_user.id)
        if action.status == ActionStatus.INVITED:
            action.status = ActionStatus.REJECTED
            await self.db.commit()
            logging.info("Invitation rejected")
        else:
            raise HTTPException(
                status_code=409, detail="Invitation already accepted")

    async def get_member(self, company_id: UUID, user_id: UUID):
        company_member = await self.db.execute(select(CompanyMember).where(CompanyMember.company_id == company_id).where(CompanyMember.user_id == user_id))
        company_member = company_member.scalars().first()
        if not company_member:
            raise HTTPException(
                status_code=404, detail="User not member of company")
        return company_member

    async def exit_from_company(self, company_id: UUID, current_user: User) -> None:
        company_member = await self.get_member(company_id, current_user.id)
        await self.db.delete(company_member)
        await self.db.commit()
        logging.info("User exited from company")

    async def get_invited_users(self, company_id: UUID):
        invited_users = await self.db.execute(select(Action.user_id).where(Action.company_id == company_id).where(Action.status == ActionStatus.INVITED))
        invited_users = invited_users.scalars().all()
        if not invited_users:
            raise HTTPException(
                status_code=404, detail="No invited users found")
        return invited_users

    async def get_requested_users(self, company_id: UUID):
        requested_users = await self.db.execute(select(Action.user_id).where(Action.company_id == company_id).where(Action.status == ActionStatus.REQUESTED))
        requested_users = requested_users.scalars().all()
        if not requested_users:
            raise HTTPException(
                status_code=404, detail="No requested users found")
        return requested_users

    async def get_company_members(self, company_id: UUID):
        company_members = await self.db.execute(select(CompanyMember.user_id).where(CompanyMember.company_id == company_id))
        company_members = company_members.scalars().all()
        if not company_members:
            raise HTTPException(status_code=404, detail="No members found")
        return company_members

    async def send_join_request(self, company_id: UUID, user_id: UUID) -> None:
        await self.get_company_by_id(company_id)
        request_creation = Action(
            company_id=company_id, user_id=user_id, status=ActionStatus.REQUESTED)
        self.db.add(request_creation)
        await self.db.commit()
        await self.db.refresh(request_creation)
        logging.info(f"Join request sent to company with id {company_id}")

    async def cancel_join_request(self, company_id: UUID, user_id: UUID) -> None:
        request = await self.get_request(company_id, user_id)
        await self.db.delete(request)
        await self.db.commit()
        logging.info("Join request cancelled")

    async def reject_join_request(self, company_id: UUID, user_id: UUID) -> None:
        request = await self.get_request(company_id, user_id)
        if request.status == ActionStatus.REQUESTED:
            request.status = ActionStatus.REJECTED
            await self.db.commit()
            logging.info("Join request rejected")

    # be-1
    async def get_user_role_in_company(self, company_id: UUID, user_id: UUID) -> str:
        company_member = await self.db.execute(select(CompanyMember).where(CompanyMember.company_id == company_id).where(CompanyMember.user_id == user_id))
        company_member = company_member.scalars().first()
        if not company_member:
            raise HTTPException(
                status_code=404, detail="User not member of company")
        return company_member.role
    
    async def promote_user_to_admin(self, company_id: UUID, user_id: UUID) -> None:
        company_member = await self.get_member(company_id, user_id)
        if company_member.role == Role.MEMBER:
            company_member.role = Role.ADMIN
            await self.db.commit()
            logging.info("User promoted to admin")
        else:
            raise HTTPException(
                status_code=400, detail="User is already an admin or owner")
        
    async def demote_admin_to_member(self, company_id: UUID, user_id: UUID) -> None:
        company_member = await self.get_member(company_id, user_id)
        if company_member.role == Role.ADMIN:
            company_member.role = Role.MEMBER
            await self.db.commit()
            logging.info("Admin demoted to user")
        else:
            raise HTTPException(
                status_code=400, detail="User is already a member or owner")
        
    async def get_company_admins(self, company_id: UUID):
        company_admins = await self.db.execute(select(CompanyMember.user_id).where(CompanyMember.company_id == company_id).where(CompanyMember.role == Role.ADMIN))
        company_admins = company_admins.scalars().all()
        if not company_admins:
            raise HTTPException(
                status_code=404, detail="No admins found")
        return company_admins

        
