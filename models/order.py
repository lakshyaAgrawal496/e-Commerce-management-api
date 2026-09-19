from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from utils.enums import OrderStatus
from datetime import datetime

class OrderItemResponse(BaseModel):
    product_id : int
    product_name : str
    unit_price : Decimal
    quantity : int
 
    model_config = ConfigDict(from_attributes=True)
 
class OrderResponse(BaseModel):
    user_id : int
    ordered_at : datetime
    order_id : int
    payment_id : int | None
    order_status : OrderStatus
    total_amount : Decimal
    discounted_amount : Decimal
    final_amount : Decimal
    items : list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)



    