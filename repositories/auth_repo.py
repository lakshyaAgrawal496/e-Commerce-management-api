from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import User

class AuthRepo:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create_user(self, user:User):
        self.db.add(user)
        await self.db.commit()
        return user

    async def get_user(self,email):
        result = await self.db.execute(select(User).where(User.email==email))
        return result.scalar_one_or_none()

 

