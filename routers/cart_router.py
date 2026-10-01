from fastapi import APIRouter, Path
from fastapi import status
from dependencies import db_dependency
from utils.auth import user_dependency
from services import CartService, CheckoutService
from models.cart import CartItemRequest
from utils.response import success_response

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)

@router.post("")
async def add_to_cart(db:db_dependency, user:user_dependency, cart_item:CartItemRequest):
    cart_service = CartService(db)
    user_id = user["user_id"]
    cart = await cart_service.add_to_cart(user_id,cart_item)
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Product Added to cart successfully",
        data=cart
    )

@router.get("")
async def get_cart(db:db_dependency, user:user_dependency):
    checkout_service = CheckoutService(db)
    user_id = user["user_id"]
    checkout_data = await checkout_service.checkout(user_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Your cart checkout is ready",
        data=checkout_data
    )

@router.delete("/{product_id}")
async def remove_from_cart(db:db_dependency, user:user_dependency, product_id:int=Path(gt=0)):
    cart_service = CartService(db)
    user_id = user["user_id"]
    await cart_service.remove_from_cart(user_id,product_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Cart deleted successfully"
    )
