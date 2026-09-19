from sqlalchemy.ext.asyncio import AsyncSession
from schemas import Payment
from sqlalchemy import select

class PaymentRepo:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create_payment(self,payment:Payment):
        self.db.add(payment)
        await self.db.flush()
        return payment

    async def get_payment(self,payment_id:int):
        result = await self.db.execute(select(Payment).where(Payment.payment_id==payment_id))
        return result.scalar_one_or_none()

