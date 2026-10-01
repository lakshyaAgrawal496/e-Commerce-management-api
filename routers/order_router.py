from fastapi import APIRouter, Path, Query
from fastapi import status
from dependencies import db_dependency
from utils.auth import user_dependency, admin_dependency
from services import OrderService
from utils.enums import PaymentMethod, OrderUpdateStatus
from utils.response import success_response
from models import ReturnOrderRequest

router = APIRouter(
    prefix="/orders",
    tags=["Order"]
)

@router.post("")
async def place_order(db:db_dependency, user:user_dependency, method:PaymentMethod):
    order_service = OrderService(db)
    user_id = user["user_id"]
    order = await order_service.place_order(user_id,method)
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Order placed successfully",
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

@router.patch("/{order_id}/cancel")
async def cancel_order(db:db_dependency, user:user_dependency, order_id:int=Path(gt=0)):
    order_service = OrderService(db)
    user_id = user["user_id"]
    cancelled_order = await order_service.cancel_order(order_id,user_id)
    return success_response(
            status_code=status.HTTP_200_OK,
            message="Order cancelled successfully",
            data=cancelled_order
        )

@router.post("/{order_id}/return")
async def return_order(db:db_dependency,user:user_dependency, order_id:int, order:ReturnOrderRequest):
    order_service = OrderService(db)
    user_id = user["user_id"]
    returned_order = await order_service.return_order(user_id,order_id,order)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Order return has been successfully initiated",
        data=returned_order
    )

@router.get("")
async def get_all_orders(db:db_dependency,user:user_dependency):
    order_service = OrderService(db)
    role=user["role"]
    if role=="admin":
        order = await order_service.get_all_orders()
    else:
        user_id=user["user_id"]
        order = await order_service.get_order_history(user_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Orders fetched successfully",
        data=order
    )

@router.patch("/{order_id}")
async def update_order_status(db:db_dependency,user:admin_dependency,order_status:OrderUpdateStatus,order_id:int=Path(gt=0)):
    order_service = OrderService(db)
    updated_order = await order_service.update_order_status(order_id,order_status)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Order status has been updated successfully",
        data=updated_order
    )