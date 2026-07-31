import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not configured."
    )


if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+asyncpg://",
        1,
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

async def initialize_database():
    async with engine.begin() as conn:
        await conn.exec_driver_sql(
            """
            ALTER TABLE jobs
            ADD COLUMN IF NOT EXISTS retry_seconds INTEGER NOT NULL DEFAULT 0
            """
        )

        await conn.exec_driver_sql(
            """
            ALTER TABLE jobs
            ADD COLUMN IF NOT EXISTS retry_message VARCHAR(255)
            """
        )

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with SessionLocal() as session:
        yield session
