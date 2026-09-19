from sqlalchemy.ext.asyncio import AsyncSession
from models import ProductRequest, ProductResponse
from schemas import Product
from repositories import ProductRepo
from exceptions import ProductNotFoundError
import logging

logger = logging.getLogger("GrocerEase.product_service")
 
class ProductService:
    def __init__(self,db:AsyncSession):
        self.product_repo = ProductRepo(db)

    async def create_product(self,product:ProductRequest):
        product_data = Product(**product.model_dump())
        created_product = await self.product_repo.create_product(product_data)
        logger.info(f"Product created successfully productID: {created_product.product_id}")
        return ProductResponse.model_validate(created_product)

    async def get_product_by_search_term(self,search_term:str):
        result = await self.product_repo.get_product_by_search_term(search_term)
        if not result:
            logger.warning(f"Product not found for the search term: {search_term}")
            raise ProductNotFoundError()
        logger.info(f"Products with search term: {search_term} are fetched successfully")
        return [ProductResponse.model_validate(product) for product in result]

    async def get_product_by_id(self,product_id:int):
        result = await self.product_repo.get_product_by_id(product_id)
        if result is None:
            logger.warning(f"Product not found - product_id: {product_id}")
            raise ProductNotFoundError()
        logger.info("Product has been fetched successfully")
        return ProductResponse.model_validate(result)
        