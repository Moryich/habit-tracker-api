from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_users(self):
        return await self.repo.get_all()
