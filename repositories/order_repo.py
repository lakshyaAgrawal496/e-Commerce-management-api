from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas import Order, OrderItem, ReturnOrder
from utils.enums import OrderStatus
from sqlalchemy.orm import selectinload
 
class OrderRepo:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create_order(self,order:Order):
        self.db.add(order)
        await self.db.flush()
        return order

    async def add_order_item(self,order_item:OrderItem):
        self.db.add(order_item)
        await self.db.flush()
        return order_item

    async def get_order(self, order_id:int, user_id:int):
        result = await self.db.execute(select(Order).options(selectinload(Order.payment),selectinload(Order.items)\
                                              .selectinload(OrderItem.product))\
                                                .where(Order.order_id==order_id)\
                                                    .where(Order.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_order_history(self, user_id:int):
        result = await self.db.execute(select(Order).options(selectinload(Order.payment),selectinload(Order.items)\
                                              .selectinload(OrderItem.product))\
                                                .where(Order.user_id==user_id))
        return result.scalars().all()
    
    async def get_all_orders(self):
        result = await self.db.execute(select(Order).options(selectinload(Order.payment),selectinload(Order.items)\
                                              .selectinload(OrderItem.product)))
        return result.scalars().all()

    async def update_order_status(self, order:Order, status:OrderStatus):
        order.status = status
        await self.db.flush()

    async def get_return_order(self, order_id: int):
        result = await self.db.execute(select(ReturnOrder).where(ReturnOrder.order_id == order_id))
        return result.scalar_one_or_none()

    async def create_return_order(self, return_order: ReturnOrder):
        self.db.add(return_order)
        await self.db.flush()
        return return_order
        