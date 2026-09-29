from datetime import datetime

from app.repositories.habit_repository import HabitRepository
from app.schemas.habit import HabitChange, HabitCreate
from app.core.exceptions import SomethingAlreadyExistsException, SomethingIsInvalidException, SomethingNotFoundException 

class HabitService:
    def __init__(self, repo: HabitRepository):
        self.repo = repo

    async def create(self, habit: HabitCreate, user_id: int):
        exists = await self.repo.get_by_user_id_and_name(user_id, habit.name)
        if exists:
            raise SomethingAlreadyExistsException('This habit is already in use')
        new_habit = await self.repo.create(habit.name, habit.days)
        return new_habit

    async def delete_habit(self, id: int):
        exists = await self.repo.get_by_id(id)
        if not exists:
            raise SomethingNotFoundException('Habit not found')
        await self.repo.delete(exists)

    async def change_habit_days(self, id: int, habit: HabitChange):
        exists = await self.repo.get_by_id(id)
        if not exists:
            raise SomethingNotFoundException('Habit not found')
        new_habit = await self.repo.change_days(exists, habit)
        return new_habit

    async def check_in(self, id: int):
        habit_data = await self.repo.get_by_id(id)
        if not habit_data:
            raise SomethingNotFoundException('Habit not found')
        now = datetime.now().isoweekday()
        if now not in habit_data.days:
            raise SomethingIsInvalidException("This is not the day")
        if now in habit_data.checked_days:
            raise SomethingAlreadyExistsException("This day is already checked")
        new_habit = await self.repo.add_checked_days(habit_data, now)
        return new_habit

    async def get_by_user_id(self, user_id: int):
        return await self.repo.get_by_user_id(user_id)

    async def reset_all_checked_days(self):
        return await self.repo.reset_all_checked_days()
