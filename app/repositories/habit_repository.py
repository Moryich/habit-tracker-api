from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.habit import Habit
from app.schemas.habit import HabitChange

class HabitRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user_id_and_name(self, user_id: int, name: str) -> Habit | None:
        return (await self.db.execute(select(Habit).where(Habit.user_id == user_id).where(Habit.name == name))).scalar_one_or_none()

    async def get_by_id(self, id: int) -> Habit | None:
        return (await self.db.execute(select(Habit).where(Habit.id == id))).scalar_one_or_none()

    async def create(self, name: str, days: list[int], user_id: int) -> Habit:
        new_habit = Habit(
            user_id = user_id,
            name = name,
            days = days
        )
        self.db.add(new_habit)
        await self.db.commit()
        await self.db.refresh(new_habit)
        return new_habit

    async def delete(self, habit: Habit) -> None:
        await self.db.delete(habit)
        await self.db.commit()

    async def change_days(self, habit: Habit, habit_change: HabitChange) -> Habit:
        habit.days = habit_change.days
        habit.checked_days = []
        await self.db.commit()
        await self.db.refresh(habit)
        return habit 

    async def add_checked_days(self, habit: Habit, now: int) -> Habit:
        habit.checked_days = habit.checked_days + [now]
        await self.db.commit()
        await self.db.refresh(habit)
        return habit

    async def get_all(self):
        return (await self.db.execute(select(Habit))).scalars().all()

    async def get_by_user_id(self, user_id):
        return (await self.db.execute(select(Habit).where(Habit.user_id == user_id))).scalars().all()

    async def reset_all_checked_days(self):
        await self.db.execute(update(Habit).values(checked_days=[]))
        await self.db.commit()
