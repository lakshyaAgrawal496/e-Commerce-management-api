from fastapi import APIRouter, status, Query, Path
from dependencies import db_dependency
from utils.auth import user_dependency, admin_dependency
from models.product import ProductRequest
from services import ProductService
from utils.response import success_response

router = APIRouter(
    prefix="/product",
    tags=["Product"]
)

@router.post("")
async def create_product(product:ProductRequest, db:db_dependency, current_user:admin_dependency):
    product_service = ProductService(db)
    product = await product_service.create_product(product)
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Product created successfully",
        data=product
    )

@router.get("/search")
async def get_product_by_search_term(db:db_dependency, current_user:user_dependency, search_term:str=Query(min_length=1)):
    product_service = ProductService(db)
    products = await product_service.get_product_by_search_term(search_term)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Products fetched successfully",
        data=products
    )

@router.get("/{product_id}")
async def get_product_by_id(db:db_dependency, current_user:user_dependency,product_id:int=Path(gt=0)):
    product_service = ProductService(db)
    product = await product_service.get_product_by_id(product_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Product fetched successfully",
        data=product
    )
    