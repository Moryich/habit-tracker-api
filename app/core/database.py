from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import config

class Base(DeclarativeBase):
    pass

engine = create_async_engine(config.DATABASE_URL)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    db = Session()
    try:
        yield db
    finally:
        await db.close()
