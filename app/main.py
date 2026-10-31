from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.exceptions import AppException
from app.routes.user import user
from app.routes.habit import habit
from app.routes.auth import auth
from app.core.config import get_database_settings, get_redis_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(get_database_settings().DATABASE_URL)
    Session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    redis = Redis.from_url(f"{get_redis_settings().REDIS_URL}/1")
   
    app.state.session_factory = Session
    app.state.redis = redis

    try:
        yield
    finally:
        try:
            await redis.aclose()
        finally:
            await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(habit)
app.include_router(auth)
app.include_router(user)

@app.exception_handler(AppException)
def exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, AppException):
        raise exc
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
