from schemas import Cart, CartItem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select


class CartRepo:
    def __init__(self,db:AsyncSession):
        self.db = db
 
    async def create_cart(self,user_id:int):
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        await self.db.flush()
        return cart
     
    async def add_to_cart(self, cart_item:CartItem):
        self.db.add(cart_item)
        await self.db.flush()
        return cart_item
 
    async def get_cart_item(self,product_id:int, cart_id:int):
        result = await self.db.execute(select(CartItem).where(CartItem.product_id==product_id).where(CartItem.cart_id==cart_id))
        return result.scalar_one_or_none()

    async def get_cart(self, user_id):
        cart = await self.db.execute(select(Cart).options(selectinload(Cart.items).selectinload(CartItem.product)).execution_options(populate_existing=True)\
                                     .where(Cart.user_id==user_id))
        return cart.scalar_one_or_none()

    async def update_cart_item(self,product_id,cart_id,new_quantity:int):
        cart_item = await self.get_cart_item(product_id,cart_id)
        cart_item.quantity = new_quantity
        await self.db.flush()
        return cart_item

    async def remove_from_cart(self, cart_item:CartItem):
        await self.db.delete(cart_item)
        await self.db.flush()

