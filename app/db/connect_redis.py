import asyncio
from app.core.config import Settings
import aioredis


settings = Settings()


import aioredis

class RedisClient:

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

asyncio.run(store_data_in_redis())

asyncio.run(retrieve_data_from_redis())

asyncio.run(check_redis_connection())