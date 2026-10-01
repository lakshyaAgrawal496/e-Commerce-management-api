from fastapi import APIRouter, status, Path, Query
from dependencies import db_dependency
from utils.auth import user_dependency, admin_dependency
from models.inventory import InventoryRequest
from services import InventoryService
from utils.response import success_response

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)

@router.post("")
async def add_inventory(inventory:InventoryRequest, db:db_dependency, user:admin_dependency):
    inventory_service = InventoryService(db)
    inven = await inventory_service.add_inventory(inventory)
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Inventory created successfully",
        data=inven
    )

@router.get("")
async def get_inventory(db:db_dependency, user:user_dependency):
    inventory_service = InventoryService(db)
    inventory = await inventory_service.get_all_inventory()
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Inventory fetched successfully",
        data=inventory
    )

@router.get("/{product_id}")
async def get_inventory(db:db_dependency, user:user_dependency, product_id:int=Path(gt=0)):
    inventory_service = InventoryService(db)
    inventory = await inventory_service.get_inventory(product_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Inventory fetched successfully",
        data=inventory
    )

@router.patch("/{product_id}")
async def update_inventory_quantity(db:db_dependency, user:admin_dependency,product_id:int=Path(gt=0), new_quantity:int=Query(ge=0)):
    inventory_service = InventoryService(db)
    inventory = await inventory_service.update_inventory_quantity(product_id,new_quantity)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Inventory quantity updated successfully",
        data=inventory
    )





