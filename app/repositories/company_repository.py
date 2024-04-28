from app.db.user_models import Company ,Invitations, InviteStatus,RequestsStatus, Company_Members ,Requests
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from app.db.user_models import User
import logging
from sqlalchemy.exc import DBAPIError
from uuid import UUID
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError
from app.db.user_models import Invitations, InviteStatus ,Company_Members
from sqlalchemy.sql import text


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
        return None

    async def update_company(self, company_id: UUID, company_data: dict) -> Company:
        company = await self.get_company_without_visability(company_id)
        for key, value in company_data.items():
            setattr(company, key, value)
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def invite_user_to_company(self, company_id: UUID, user_id: UUID) -> None:
        await self.db.execute(text('DROP TYPE IF EXISTS invitation_status;'))
        company = await self.get_company_without_visability(company_id)
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        company_id = company.id
        user_id = user.id
        invitation_creation = Invitations(company_id=company_id, user_id=user_id, status=InviteStatus.PENDING)
        self.db.add(invitation_creation)
        await self.db.commit()
        await self.db.refresh(invitation_creation)
        logging.info("User invited to company")
        return None
    
    async def cancel_invitation(self, company_id: UUID, user_id: UUID) -> None:
        invitation = await self.db.execute(select(Invitations).where(Invitations.company_id == company_id).where(Invitations.user_id == user_id))
        invitation = invitation.scalars().first()
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found")
        await self.db.delete(invitation)
        await self.db.commit()
        logging.info("Invitation cancelled")
        return None
    
    async def check_if_user_is_member_of_company_for_deleting(self, company_id: UUID, user_id: UUID) -> None:
        company_member = await self.db.execute(select(Company_Members).where(Company_Members.company_id == company_id).where(Company_Members.user_id == user_id))
        company_member = company_member.scalars().first()
        return company_member

    
    async def check_if_user_is_member_of_company(self, company_id: UUID, user_id: UUID) -> None:
        company_member = await self.check_if_user_is_member_of_company_for_deleting(company_id, user_id)
        if company_member:
            raise HTTPException(status_code=404, detail="User already member of company")
        return None
    
    async def check_if_user_invited_already(self, company_id: UUID, user_id: UUID) -> None:
        invitation = await self.db.execute(select(Invitations).where(Invitations.company_id == company_id).where(Invitations.user_id == user_id))
        invitation = invitation.scalars().first()
        if invitation:
            raise HTTPException(status_code=404, detail="User already invited")
        return None
    
    async def check_if_user_requested_already(self, company_id: UUID, user_id: UUID) -> None:
        request = await self.db.execute(select(Requests).where(Requests.company_id == company_id).where(Requests.user_id == user_id))
        request = request.scalars().first()
        if request:
            raise HTTPException(status_code=404, detail="User already requested")
        return None
    
    async def accept_invitation(self, company_id: UUID, current_user: User) -> None:
        invitation = await self.db.execute(select(Invitations).where(Invitations.company_id == company_id).where(Invitations.user_id == current_user.id))
        invitation = invitation.scalars().first()
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found")
        if invitation.status == InviteStatus.PENDING:
            invitation.status = InviteStatus.ACCEPTED
            company_member_adding = Company_Members(company_id=company_id, user_id=current_user.id)
            self.db.add(company_member_adding)
            await self.db.commit()
            await self.db.refresh(company_member_adding)
            logging.info("Invitation accepted")
            return None
        else:
            raise HTTPException(status_code=404, detail="Invitation already accepted")
        
    async def reject_invitation(self, company_id: UUID, current_user: User) -> None:
        invitation = await self.db.execute(select(Invitations).where(Invitations.company_id == company_id).where(Invitations.user_id == current_user.id))
        invitation = invitation.scalars().first()
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found")
        if invitation.status == InviteStatus.PENDING:
            invitation.status = InviteStatus.REJECTED
            await self.db.commit()
            logging.info("Invitation rejected")
            return None
        else:
            raise HTTPException(status_code=404, detail="Invitation already accepted")
        

    async def delete_user_from_company(self, company_id: UUID, user_id: UUID) -> None:
        company_member = await self.db.execute(select(Company_Members).where(Company_Members.company_id == company_id).where(Company_Members.user_id == user_id))
        company_member = company_member.scalars().first()
        if not company_member:
            raise HTTPException(status_code=404, detail="User not member of company")
        await self.db.delete(company_member)
        await self.db.commit()
        await self.db.refresh(company_member)
        await self.cancel_invitation(company_id, user_id)
        logging.info("User deleted from company")
        return None
    
        
    
    async def exit_from_company(self, company_id: UUID, current_user: User) -> None:
        company_member = await self.db.execute(select(Company_Members).where(Company_Members.company_id == company_id).where(Company_Members.user_id == current_user.id))
        company_member = company_member.scalars().first()
        if not company_member:
            raise HTTPException(status_code=404, detail="User not member of company")
        await self.db.delete(company_member)
        await self.db.commit()
        logging.info("User exited from company")
        return None
    
    async def get_invited_users(self, company_id: UUID):
        invited_users = await self.db.execute(select(Invitations.user_id).where(Invitations.company_id == company_id))
        invited_users = invited_users.scalars().all()
        if not invited_users:
            raise HTTPException(status_code=404, detail="No invited users found")
        return invited_users
    
    async def get_requested_users(self, company_id: UUID):
        requested_users = await self.db.execute(select(Requests.user_id).where(Requests.company_id == company_id))
        requested_users = requested_users.scalars().all()
        if not requested_users:
            raise HTTPException(status_code=404, detail="No requested users found")
        return requested_users
    
    async def get_company_members(self, company_id: UUID):
        company_members = await self.db.execute(select(Company_Members.user_id).where(Company_Members.company_id == company_id))
        company_members = company_members.scalars().all()
        if not company_members:
            raise HTTPException(status_code=404, detail="No members found")
        return company_members
        

    async def send_join_request(self, company_id: UUID, user_id: UUID) -> None:
        await self.get_company_by_id(company_id)
        request_creation = Requests(company_id=company_id, user_id=user_id, status=RequestsStatus.PENDING)
        self.db.add(request_creation)
        await self.db.commit()
        await self.db.refresh(request_creation)
        logging.info(f"Join request sent to company with id {company_id}")
        return None
    
    async def cancel_join_request(self, company_id: UUID, user_id: UUID) -> None:
        request = await self.db.execute(select(Requests).where(Requests.company_id == company_id).where(Requests.user_id == user_id))
        request = request.scalars().first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        await self.db.delete(request)
        await self.db.commit()
        logging.info("Join request cancelled")
        return None
    
    async def accept_join_request(self, company_id: UUID, user_id: UUID) -> None:
        request = await self.db.execute(select(Requests).where(Requests.company_id == company_id).where(Requests.user_id == user_id))
        request = request.scalars().first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        if request.status == RequestsStatus.PENDING:
            request.status = RequestsStatus.ACCEPTED
            company_member_adding = Company_Members(company_id=company_id, user_id=user_id)
            self.db.add(company_member_adding)
            await self.db.commit()
            await self.db.refresh(company_member_adding)
            logging.info("Join request accepted")
            return None
        else:
            raise HTTPException(status_code=404, detail="Request already accepted")
        

    async def reject_join_request(self, company_id: UUID, user_id: UUID) -> None:
        request = await self.db.execute(select(Requests).where(Requests.company_id == company_id).where(Requests.user_id == user_id))
        request = request.scalars().first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        if request.status == RequestsStatus.PENDING:
            request.status = RequestsStatus.REJECTED
            await self.db.commit()
            logging.info("Join request rejected")
            return None
    

    

    
