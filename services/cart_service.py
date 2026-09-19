from models import CartItemRequest,CartResponse, CartItemResponse
from schemas.cart import CartItem
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import InventoryRepo, CartRepo
from exceptions import CartNotFoundError,CartItemNotFoundError,InventoryNotFoundError,InsufficientStockError
import logging

logger = logging.getLogger("GrocerEase.cart_service")

class CartService:
    def __init__(self, db:AsyncSession):
        self.db = db
        self.cart_repo = CartRepo(db)
        self.inventory_repo = InventoryRepo(db)

    def orm_to_cart_response(self,cart):
        return CartResponse(
            cart_id=cart.cart_id,
            items=[
                CartItemResponse(
                    product_id=item.product_id,
                    product_name=item.product.product_name,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                )
                for item in cart.items
            ]
        )

    async def get_cart(self,user_id:int):
        cart = await self.cart_repo.get_cart(user_id)
        if cart is None:
            logger.warning(f"Cart not found - user_id={user_id}")
            raise CartNotFoundError()

        logger.info(f"Cart fetched successfully - user_id={user_id} cart_id={cart.cart_id}")
        return self.orm_to_cart_response(cart)

    async def add_to_cart(self, user_id:int, cart_item:CartItemRequest):
        async with self.db.begin():
            inventory = await self.inventory_repo.get_inventory(cart_item.product_id)
            if inventory is None:
                logger.warning(f"Add to cart failed: inventory not found - product_id={cart_item.product_id}")
                raise InventoryNotFoundError()

            cart = await self.cart_repo.get_cart(user_id)
            if cart is None:
                cart = await self.cart_repo.create_cart(user_id)
                logger.info(f"Cart created successfully - user_id={user_id} cart_id={cart.cart_id}")

            existing_item = await self.cart_repo.get_cart_item(cart_item.product_id,cart.cart_id)
            if existing_item:
                final_quantity = existing_item.quantity + cart_item.quantity
            else:
                final_quantity = cart_item.quantity

            if inventory.quantity<final_quantity:
                logger.warning(f"Add to cart failed: insufficient inventory")
                raise InsufficientStockError()
    
            if existing_item:
                await self.cart_repo.update_cart_item(cart_item.product_id,cart.cart_id,final_quantity)
            else:
                item = CartItem(
                    cart_id = cart.cart_id,
                    product_id = cart_item.product_id,
                    quantity = final_quantity
                )
                await self.cart_repo.add_to_cart(item)
            logger.info(f"Product added to cart successfully - user_id={user_id} cart_id={cart.cart_id}")
            cart = await self.cart_repo.get_cart(user_id)
            return self.orm_to_cart_response(cart)

    async def remove_from_cart(self,user_id:int, product_id:int):
        async with self.db.begin():
            cart = await self.cart_repo.get_cart(user_id)
            if cart is None:
                logger.warning(f"Cart not found for userID: {user_id}")
                raise CartNotFoundError()
            
            item = await self.cart_repo.get_cart_item(product_id,cart.cart_id)
            if item is None:
                logger.warning(f"Remove from cart failed: product not found in cart - user_id={user_id}")
                raise CartItemNotFoundError()
            
            await self.cart_repo.remove_from_cart(item)
            logger.info(f"Product removed from cart successfully - user_id={user_id}")
            
            cart = await self.cart_repo.get_cart(user_id)
            return self.orm_to_cart_response(cart)
