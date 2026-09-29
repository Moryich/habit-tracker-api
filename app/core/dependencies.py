from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import InvalidCredentialsException, SomethingIsForbiddenException, SomethingNotFoundException
from app.core.security import decode_access_token
from app.repositories.habit_repository import HabitRepository

def get_habit_repository(db: AsyncSession = Depends(get_db)) -> HabitRepository:
    return HabitRepository(db)

http_bearer = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
    token = credentials.credentials
    try:
        user_data = decode_access_token(token)
        return user_data
    except JWTError:
        raise InvalidCredentialsException("Unauthorized")

async def require_id(habit_id: int, user = Depends(get_current_user), repo = Depends(get_habit_repository)):
    habit = await repo.get_by_id(habit_id)
    if not habit:
        raise SomethingNotFoundException("Habit not found")
    if int(user["sub"]) != habit.user_id:
        raise SomethingIsForbiddenException("Forbidden")
