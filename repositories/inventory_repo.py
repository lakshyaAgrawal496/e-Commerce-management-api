from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import Inventory
from sqlalchemy.orm import selectinload

class InventoryRepo:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def add_inventory(self, inventory:Inventory):
        self.db.add(inventory)
        await self.db.flush()
        return inventory

    async def get_all_inventory(self):
        result = await self.db.execute(select(Inventory).options(selectinload(Inventory.product)))
        return result.scalars().all()

    async def get_inventory(self, product_id:int):
        result = await self.db.execute(select(Inventory).options(selectinload(Inventory.product)).where(Inventory.product_id==product_id))
        return result.scalar_one_or_none()
    
    async def get_inventory_for_update(self, product_id: int):
        result = await self.db.execute(select(Inventory).options(selectinload(Inventory.product))\
                                       .where(Inventory.product_id == product_id).with_for_update().execution_options(populate_existing=True))
        return result.scalar_one_or_none()

    async def update_inventory_quantity(self, inventory:Inventory, new_quantity:int):
        inventory.quantity = new_quantity
        await self.db.flush()
        return inventory
    