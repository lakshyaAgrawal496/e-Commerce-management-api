from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class CheckoutItem(BaseModel):
    cart_id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int

class CheckoutResponse(BaseModel):
    cart_id : int
    total_amount : Decimal
    discounted_amount : Decimal
    final_amount : Decimal
    items : list[CheckoutItem]

    model_config = ConfigDict(from_attributes=True)