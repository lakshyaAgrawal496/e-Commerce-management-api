from sqlalchemy.ext.asyncio import AsyncSession
from repositories import CartRepo , InventoryRepo
from models import CheckoutResponse, CheckoutItem
from exceptions import CartNotFoundError, CartItemNotFoundError,InsufficientStockError,InventoryNotFoundError
from decimal import Decimal
import logging

logger = logging.getLogger("GrocerEase.checkout_service")

class CheckoutService:
    def __init__(self,db:AsyncSession):
        self.db = db
        self.cart_repo = CartRepo(db)
        self.inventory_repo = InventoryRepo(db)

    @staticmethod
    def discount(total:Decimal):
        if total<2000:
            return Decimal("0")
        if total>=2000 and total<5000:
            return total*Decimal("0.1")
        elif total>=5000 and total<8000:
            return total*Decimal("0.2")
        else:
            return total*Decimal("0.3")

    async def checkout(self, user_id: int):
        cart = await self.cart_repo.get_cart(user_id)
        if cart is None:
            logger.warning(f"Checkout failed: cart not found - user_id={user_id}")
            raise CartNotFoundError()
        if not cart.items:
            logger.warning(f"Checkout failed: cart is empty - user_id={user_id}")
            raise CartItemNotFoundError()

        total_amount = Decimal("0")

        for item in cart.items:
            inventory = await self.inventory_repo.get_inventory(item.product_id)
            if inventory is None:
                logger.warning(f"Checkout failed: inventory not found - product_id={item.product_id}")
                raise InventoryNotFoundError()
            if inventory.quantity < item.quantity:
                logger.warning(f"Checkout failed: insufficient inventory - product_id={item.product_id} requested={item.quantity} available={inventory.quantity}")
                raise InsufficientStockError()

            total_amount+=item.product.unit_price * item.quantity

        discounted_amount = self.discount(total_amount)
        final_amount = total_amount-discounted_amount 

        logger.info(f"Checkout calculated successfully - user_id={user_id} cart_id={cart.cart_id}")
        return CheckoutResponse(
            cart_id=cart.cart_id,
            total_amount=total_amount,
            discounted_amount=discounted_amount,
            final_amount=final_amount,
            items=[CheckoutItem(
                cart_id=item.cart_id,
                product_id=item.product_id,
                product_name=item.product.product_name,
                unit_price=item.product.unit_price,
                quantity=item.quantity
            ) for item in cart.items]
        )
        
        