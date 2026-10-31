import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.celery_app import celery_app
from app.repositories.habit_repository import HabitRepository
from app.services.habitService import HabitService
from app.core.config import get_database_settings

@celery_app.task
def weekly_reset():
    asyncio.run(reset_all_checked_days())

async def reset_all_checked_days():
    engine = create_async_engine(get_database_settings().DATABASE_URL)
    Session = async_sessionmaker(bind=engine, expire_on_commit=False)
    try:
        async with Session() as session:
            repo = HabitRepository(session)
            service = HabitService(repo)
            await service.reset_all_checked_days()
    finally:
        await engine.dispose()
