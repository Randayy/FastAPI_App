import asyncio
from app.core.config import Settings
import aioredis


settings = Settings()


class RedisClient:
    def __init__(self):
        self._redis = None

    async def connect(self):
        self._redis = await aioredis.from_url(f'redis://{settings.redis_host}:{settings.redis_port}')

    async def close(self):
        if self._redis:
            self._redis.close()
            await self._redis.wait_closed()

    async def get_redis(self):
        if not self._redis:
            await self.connect()
        return self._redis
    
    async def get_data(self, key):
        redis = await self.get_redis()
        data = await redis.get(key)
        return data
    
    async def set_data(self, key, value,expire_time=172800):
        redis = await self.get_redis()
        await redis.set(key, value)
        await redis.expire(key, expire_time)


    async def scan_iter(self, match_pattern):
        redis = await self.get_redis()
        cursor = '0'
        while cursor != 0:
            cursor, keys = await redis.scan(cursor, match=match_pattern)
            for key in keys:
                yield key


    async def scan_iter(self, match_pattern):
        redis = await self.get_redis()
        cursor = '0'
        while cursor != 0:
            cursor, keys = await redis.scan(cursor, match=match_pattern)
            for key in keys:
                yield key


async def check_redis_connection():
    Redis_client = RedisClient()
    await Redis_client.connect()
    redis = await Redis_client.get_redis()
    if redis:
        return f"Connected to Redis server"

# Cheking if redis works


async def store_data_in_redis():
    Redis_client = RedisClient()
    await Redis_client.connect()
    redis = await Redis_client.get_redis()

    if redis:
        await redis.set('check', '111')
        print("Data stored")


async def retrieve_data_from_redis():
    Redis_client = RedisClient()
    await Redis_client.connect()
    redis = await Redis_client.get_redis()

    if redis:
        data = await redis.get('check')
        if data:
            print(f"Data from Redis: {data.decode('utf-8')}")
        else:
            print("Not found")

