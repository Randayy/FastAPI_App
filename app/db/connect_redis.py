import redis.asyncio as redis
from app.core.config import settings


class RedisClient:
    def __init__(self):
        self._redis = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
        # self._redis = redis.Redis()

    async def get_redis(self):
        return self._redis


redis_client = RedisClient()