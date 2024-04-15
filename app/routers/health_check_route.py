from fastapi import APIRouter
from app.db.connect_redis import check_redis_connection
from app.db.connect_postgresql import check_connection

import logging
from app.db.connect_redis import check_redis_connection
from app.db.connect_postgresql import check_connection
from fastapi import Depends
from app.db.connect_postgresql import get_session
from app.db.user_models import User
from app.schemas.schemas import UserCreateSchema


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')

router = APIRouter()

@router.get("/")
async def health_check():
    logging.info("Health check started")
    redis = await check_redis_connection()
    postgres = await check_connection()
    logging.info("Connected to Redis and PostgreSQL")
    return { 
            "status_code": 200,
            "detail": "ok",
            "result": "working",
            "redis_status": f"{redis}",
            "postgres_status": f"{postgres}"
            }

@router.post("/user")
async def create_user(user_data: UserCreateSchema, db = Depends(get_session)):
    async with get_session() as session:
        user = User(**user_data.dict())
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

