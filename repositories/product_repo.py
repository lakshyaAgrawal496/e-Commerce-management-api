from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import Product

class ProductRepo:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create_product(self,product:Product):
        self.db.add(product)
        await self.db.commit()
        return product

    async def get_product_by_search_term(self,search_term:str):
        like_term = f"%{search_term}%"
        result = await self.db.execute(select(Product).where(
            Product.product_name.like(like_term) |
            Product.category.like(like_term) |
            Product.description.like(like_term)
            ))
        return result.scalars().all()
    
    async def get_product_by_id(self,product_id:int):
        result = await self.db.execute(select(Product).where(Product.product_id==product_id))
        return result.scalar_one_or_none()

    