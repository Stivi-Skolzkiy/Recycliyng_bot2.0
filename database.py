
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.engine import URL

from config import settings


database_url = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

engine = create_async_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


async def check_database_connection():
    async with engine.connect() as connection:

        result = await connection.execute(text("SELECT version()"))
        version = result.scalar_one()

        districts = await connection.scalar(
            text("SELECT COUNT(*) FROM districts")
        )

        categories = await connection.scalar(
            text("SELECT COUNT(*) FROM categories")
        )

        points = await connection.scalar(
            text("SELECT COUNT(*) FROM points")
        )

        point_categories = await connection.scalar(
            text("SELECT COUNT(*) FROM point_categories")
        )

        return {
            "version": version,
            "districts": districts,
            "categories": categories,
            "points": points,
            "point_categories": point_categories,
        }


async def close_database():
    await engine.dispose()
