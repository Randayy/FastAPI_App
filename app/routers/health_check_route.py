from fastapi import APIRouter
import logging
from app.db.connect_redis import check_redis_connection
from app.db.connect_postgresql import check_connection


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')
health_check_router = APIRouter()


@health_check_router.get("/")
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
