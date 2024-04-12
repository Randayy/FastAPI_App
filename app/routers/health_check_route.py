from fastapi import APIRouter
from app.db.connect_redis import redis_client
from app.db.connect_postgresql import check_connection

router = APIRouter()

@router.get("/")
async def health_check():
    redis = await redis_client.get_redis()
    redis_status = await redis.ping()
    postgres = await check_connection()
    return { 
            "status_code": 200,
            "detail": "ok",
            "result": "working",
            "redis_status": f"{redis_status}",
            "postgres_status": f"{postgres}"
            }
