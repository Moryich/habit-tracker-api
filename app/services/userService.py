from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_users(self, limit: int, offset: int):
        return await self.repo.get_users(limit, offset)
