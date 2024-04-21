from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.core.config import Settings
from sqlalchemy import text


settings = Settings()

DATABASE_URL = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, class_=AsyncSession)


async def get_session():
    async with async_session() as session:
        yield session


async def check_connection():
    async with async_session() as session:
        try:
            if session:
                return f"Connected to PostgreSQL server"
        except OperationalError as e:
            return f"Failed to connect to PostgreSQL server. Error: {str(e)}"
