from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_id
from app.repositories.habit_repository import HabitRepository
from app.schemas.habit import HabitCreate, HabitChange
from app.services.habitService import HabitService

habit = APIRouter(prefix='/habit', tags=['Habit'])

def get_habit_repository(db: AsyncSession = Depends(get_db)) -> HabitRepository:
    return HabitRepository(db)

def get_habit_service(repo: HabitRepository = Depends(get_habit_repository)) -> HabitService:
    return HabitService(repo)

@habit.post('/create')
async def create(habit: HabitCreate, current_user = Depends(get_current_user), service: HabitService = Depends(get_habit_service)):
    return await service.create(habit, current_user["sub"])


@habit.delete('/delete_habit/{habit_id}')
async def delete_habit(habit_id: int, service: HabitService = Depends(get_habit_service), _ = Depends(require_id)):
    return await service.delete_habit(habit_id)

@habit.patch('/change/{habit_id}')
async def change_habit_days(habit_id: int, habit_data: HabitChange, service: HabitService = Depends(get_habit_service), _ = Depends(require_id)):
    return await service.change_habit_days(habit_id, habit_data)


@habit.patch('/checkin/{habit_id}')
async def checkin(habit_id: int, service: HabitService = Depends(get_habit_service), _ = Depends(require_id)):
    return await service.check_in(habit_id)


@habit.get('/')
async def get_all(service: HabitService = Depends(get_habit_service), current_user = Depends(get_current_user)):
    return await service.get_by_user_id(int(current_user["sub"]))
