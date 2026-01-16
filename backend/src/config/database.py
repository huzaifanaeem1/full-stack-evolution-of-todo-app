from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost:5432/todo_app")

# Ensure async driver is used for PostgreSQL connections
if DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    # Replace postgresql:// with postgresql+asyncpg:// to ensure async driver
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[12:]  # 12 is len("postgresql://")
elif DATABASE_URL.startswith("postgres://"):  # Some services use postgres:// instead of postgresql://
    # Replace postgres:// with postgresql+asyncpg:// to ensure async driver
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[11:]  # 11 is len("postgres://")

# Create async engine for PostgreSQL
async_engine = create_async_engine(DATABASE_URL)

# Create async sessionmaker
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    """Dependency for FastAPI to get async database session"""
    async with async_session() as session:
        yield session