from fastapi import APIRouter, Path, Query
from fastapi import status
from dependencies import db_dependency
from utils.auth import user_dependency, admin_dependency
from services import OrderService
from utils.enums import PaymentMethod, OrderStatus
from utils.response import success_response

router = APIRouter(
    prefix="/order",
    tags=["Order"]
)

@router.post("/place")
async def place_order(db:db_dependency, user:user_dependency, method:PaymentMethod):
    order_service = OrderService(db)
    user_id = user["user_id"]
    order = await order_service.place_order(user_id,method)
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Order placed successfully",
        data=order
    )

@router.get("/history")
async def get_order_history(db:db_dependency, user:user_dependency):
    order_service = OrderService(db)
    user_id = user["user_id"]
    order = await order_service.get_order_history(user_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Order history fetched successfully",
        data=order
    )

@router.get("/{order_id}")
async def get_order_by_id(db:db_dependency, user:user_dependency, order_id:int=Path(gt=0)):
    order_service = OrderService(db)
    user_id = user["user_id"]
    order = await order_service.get_order(order_id,user_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Order fetched successfully",
        data=order
    )

@router.patch("/cancel/{order_id}")
async def cancel_order(db:db_dependency, user:user_dependency, order_id:int=Path(gt=0)):
    order_service = OrderService(db)
    user_id = user["user_id"]
    cancelled_order = await order_service.cancel_order(order_id,user_id)
    return success_response(
            status_code=status.HTTP_200_OK,
            message="Order cancelled successfully",
            data=cancelled_order
        )

@router.post("/return/{order_id}")
async def return_order(db:db_dependency,user:user_dependency, order_id:int=Path(gt=0), reason:str=Query(min_length=5)):
    order_service = OrderService(db)
    user_id = user["user_id"]
    returned_order = await order_service.return_order(order_id,user_id,reason)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Order return has been successfully initiated",
        data=returned_order
    )

@router.get("")
async def get_all_orders_by_admin(db:db_dependency,user:admin_dependency):
    order_service = OrderService(db)
    order = await order_service.get_all_orders()
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Orders fetched successfully",
        data=order
    )

@router.patch("/status")
async def update_order_status(db:db_dependency,user:admin_dependency,order_status:OrderStatus,order_id:int=Query(gt=0),user_id:int=Query(gt=0)):
    order_service = OrderService(db)
    updated_order = await order_service.update_order_status(order_id,user_id,order_status)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Order status has been updated successfully",
        data=updated_order
    )