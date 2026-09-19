from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

class CartItemRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity : int = Field(gt=0,le=50)

class CartItemResponse(BaseModel):
    product_id : int
    product_name : str
    unit_price : Decimal
    quantity : int

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    cart_id : int
    items : list[CartItemResponse]

    model_config = ConfigDict(from_attributes=True)