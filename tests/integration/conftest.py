from fastapi import Depends, FastAPI
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from sqlalchemy.orm import exc

from app.core.config import config
from app.core.database import Base, get_db
from app.core.exceptions import AppException
from app.core.redis_client import rate_limiter, get_redis
from app.main import app, exception_handler

# test_auth_routes block
@pytest_asyncio.fixture(scope="function")
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
        try:
            yield session
        finally:
            await session.execute(text("TRUNCATE TABLE users, habits RESTART IDENTITY CASCADE"))
            await session.commit()

@pytest_asyncio.fixture(scope="function")
async def client_fixture(session_fixture, redis_client_fixture):
    async def override_get_db():
        yield session_fixture

    async def override_get_redis():
        return redis_client_fixture

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    await redis_client_fixture.delete(
        "127.0.0.1:/auth/login",
        "127.0.0.1:/auth/registration",
    )

    transport = ASGITransport(app, client=("127.0.0.1", 12345))
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        await redis_client_fixture.delete(
            "127.0.0.1:/auth/login",
            "127.0.0.1:/auth/registration",
        )
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_redis, None)

# redis mock client for limiting and brute-force protection
@pytest_asyncio.fixture(scope="function")
async def redis_client_fixture():
    redis = Redis.from_url(f"{config.TEST_REDIS_URL}/0")
    try:
        yield redis
    finally:
        await redis.aclose()

# test_rate_limiter block
@pytest_asyncio.fixture(scope="function")
async def redis_key_fixture(redis_client_fixture):
    key = f"test:rate-limit:{uuid4()}"
    try:
        yield key
    finally:
        await redis_client_fixture.delete(key)

@pytest_asyncio.fixture(scope="function")
async def redis_http_client_fixture(redis_client_fixture):
    app = FastAPI()

    def override_get_redis():
        return redis_client_fixture

    app.dependency_overrides[get_redis] = override_get_redis

    app.add_exception_handler(AppException, exception_handler)
    
    @app.get("/test-rate-limiter", dependencies=[Depends(rate_limiter(2, 5))])
    async def test_rate_limiter():
        return {"success": True}
    
    transport = ASGITransport(app, client=("127.0.0.1", 12345))

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            yield client
        finally:
            await redis_client_fixture.delete("127.0.0.1:/test-rate-limiter")

# brute-force protection block
@pytest_asyncio.fixture(scope="function")
async def brute_force_email_fixture(redis_client_fixture):
    email = "test@test.com"
    try:
        yield email
    finally:
        await redis_client_fixture.delete(f"login-failure:{email}")
