import asyncio

from app.celery_app import celery_app
from app.repositories.habit_repository import HabitRepository
from app.core.database import Session
from app.services.habitService import HabitService

@celery_app.task
def weekly_reset():
    asyncio.run(reset_all_checked_days())

async def reset_all_checked_days():
    async with Session() as session:
        repo = HabitRepository(session)
        service = HabitService(repo)
        await service.reset_all_checked_days()
