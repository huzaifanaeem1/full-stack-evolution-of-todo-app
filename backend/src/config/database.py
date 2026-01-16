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

# Handle asyncpg-specific URL parameters that cause issues
# Extract problematic query parameters that SQLAlchemy passes to asyncpg as kwargs
if "?" in DATABASE_URL and DATABASE_URL.startswith("postgresql+asyncpg"):
    base_url, query_string = DATABASE_URL.split("?", 1)
    # Split query parameters
    query_params = query_string.split("&")

    # Filter out parameters that cause issues with asyncpg
    filtered_params = []
    for param in query_params:
        if "=" in param:
            key = param.split("=")[0]
            # These parameters cause issues when passed directly to asyncpg
            if key not in ["sslmode", "channel_binding"]:
                filtered_params.append(param)

    # Reconstruct the URL with filtered parameters
    if filtered_params:
        DATABASE_URL = f"{base_url}?{'&'.join(filtered_params)}"
    else:
        DATABASE_URL = base_url

# Create async engine for PostgreSQL
async_engine = create_async_engine(DATABASE_URL)

# Create async sessionmaker
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    """Dependency for FastAPI to get async database session"""
    async with async_session() as session:
        yield session