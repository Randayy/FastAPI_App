from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.connect_postgresql import get_session
from app.db.user_models import User
from sqlalchemy import select
from app.schemas.user_schemas import SignUpRequestSchema, UserUpdateRequestSchema, UserListSchema, UserDetailSchema
from sqlalchemy.sql import text
from fastapi import HTTPException
from app.db.password_hashing import hash_password, verify_password
from fastapi import APIRouter
import logging
# fastapi_pagination-0.12.22

user_router = APIRouter()


@user_router.post("/user")
async def create_user(user_data: SignUpRequestSchema, db: AsyncSession = Depends(get_session)):
    hashed_password = hash_password(user_data.password)
    user_data_dict = user_data.dict()
    user_data_dict['password'] = hashed_password
    user = User(**user_data_dict)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logging.info(f"User {user.username} created successfully")
    
    return user


@user_router.get("/users/{user_id}", response_model=UserDetailSchema)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_session)):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user



@user_router.get("/users/",response_model=UserListSchema)
async def get_users_list(db: AsyncSession = Depends(get_session)):
    users = await db.execute(select(User))

    # check if users exist
    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    users = users.scalars().all()

    return {"message": f"All Users","users": users}


@user_router.delete("/user/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_session)):
    user = await db.get(User, user_id)
    view_user = user.__dict__.copy()

    # check if user with id exists
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    await db.commit()
    logging.info(f"User {view_user['username']} deleted successfully")

    return {"message": "User deleted successfully","user": view_user}


@user_router.put("/user/{user_id}")
async def update_user(user_id: int, user_data: UserUpdateRequestSchema, db: AsyncSession = Depends(get_session)):
    user = await db.get(User, user_id)

    # check if user with id exists
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # check if current password is correct
    if not verify_password(user_data.current_password, user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user.username = user_data.username
    user.email = user_data.email
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name

    if user_data.new_password:
        user.password = hash_password(user_data.new_password)

    await db.commit()
    await db.refresh(user)

    return {"message": "User updated successfully", "updated_user_info": user}
    

