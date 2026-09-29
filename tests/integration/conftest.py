import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport

from app.core.config import config
from app.core.database import Base, get_db
from app.main import app

@pytest_asyncio.fixture(scope="session")
async def engine_fixture():
    engine = create_async_engine(url=config.TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def session_fixture(engine_fixture):
    Session = async_sessionmaker(engine_fixture)
    async with Session() as session:
        yield session
        await session.execute(text("TRUNCATE TABLE users, habits RESTART IDENTITY CASCADE"))
        await session.commit()

@pytest_asyncio.fixture(scope="function")
async def client_fixture(session_fixture):
    async def override_get_db():
        yield session_fixture

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
