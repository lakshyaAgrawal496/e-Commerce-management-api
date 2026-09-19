from repositories import InventoryRepo, ProductRepo
from sqlalchemy.ext.asyncio import AsyncSession
from models import InventoryRequest, InventoryResponse
from schemas import Inventory
from exceptions import InventoryNotFoundError,InsufficientStockError,ProductNotFoundError
import logging

logger = logging.getLogger("GrocerEase.inventory_service")
 
class InventoryService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.inventory_repo = InventoryRepo(db)
        self.product_repo = ProductRepo(db)

    def orm_to_inventory_response(self,inventory:Inventory):
        return InventoryResponse(
            product_id=inventory.product_id,
            product_name=inventory.product.product_name,
            quantity=inventory.quantity
        )

    async def add_inventory(self,inventory:InventoryRequest):
        async with self.db.begin():
            product = await self.product_repo.get_product_by_id(inventory.product_id)
            if product is None:
                logger.warning(f"Product not found - product_id={inventory.product_id}")
                raise ProductNotFoundError()
            
            existing_inventory = await self.inventory_repo.get_inventory(inventory.product_id)
            if existing_inventory:
                new_quantity = existing_inventory.quantity + inventory.quantity
                updated_inventory = await self.inventory_repo.update_inventory_quantity(existing_inventory, new_quantity)
                logger.info(f"Inventory quantity increased - product_id={inventory.product_id} old_quantity={existing_inventory.quantity} new_quantity={new_quantity}")
                return self.orm_to_inventory_response(updated_inventory)

            inventory_data = Inventory(**inventory.model_dump())
            new_inventory = await self.inventory_repo.add_inventory(inventory_data)
            logger.info(f"Inventory created successfully - product_id={inventory.product_id} quantity={inventory.product_id}")
            return self.orm_to_inventory_response(new_inventory)

    async def get_all_inventory(self):
        inventory = await self.inventory_repo.get_all_inventory()
        if not inventory:
            logger.warning(f"Inventory is empty")
            raise InventoryNotFoundError()
        
        logger.info("Inventory is fetched successfully")
        return [self.orm_to_inventory_response(item) for item in inventory]
            
    async def get_inventory(self,product_id:int):
        inventory = await self.inventory_repo.get_inventory(product_id)
        if inventory is None:
            logger.warning(f"Inventory not found - product_id={product_id}")
            raise InventoryNotFoundError()
        
        logger.info("Inventory is fetched successfully")
        return self.orm_to_inventory_response(inventory)

    async def increment_inventory_quantity(self,product_id:int, delta:int):
        async with self.db.begin():
            inventory = await self.inventory_repo.get_inventory(product_id)
            if inventory is None:
                logger.warning(f"Inventory not found - product_id={product_id}")
                raise InventoryNotFoundError()

            new_quantity = inventory.quantity + delta
            updated_inventory = await self.inventory_repo.update_inventory_quantity(inventory,new_quantity)

            logger.info(f"Inventory incremented - product_id={product_id} new_quantity={new_quantity}")
            return self.orm_to_inventory_response(updated_inventory)
    
    async def set_inventory(self,product_id:int, new_quantity:int):
        async with self.db.begin():
            inventory = await self.inventory_repo.get_inventory(product_id)
            if inventory is None:
                logger.warning(f"Inventory not found - product_id={product_id}")
                raise InventoryNotFoundError()

            updated_inventory = await self.inventory_repo.update_inventory_quantity(inventory,new_quantity)
            logger.info(f"Inventory quantity updated - product_id={product_id} new_quantity={new_quantity}")
            return self.orm_to_inventory_response(updated_inventory)
    