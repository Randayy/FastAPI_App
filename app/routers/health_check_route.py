from fastapi import APIRouter
from app.db.connect_redis import check_redis_connection
from app.db.connect_postgresql import check_connection

router = APIRouter()

@router.get("/")
async def health_check():
    redis = await check_redis_connection()
    postgres = await check_connection()
    return { 
            "status_code": 200,
            "detail": "ok",
            "result": "working",
            "redis_status": f"{redis}",
            "postgres_status": f"{postgres}"
            }
