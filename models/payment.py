from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from utils.enums import PaymentMethod

class PaymentResponse(BaseModel):
    payment_id : int
    order_id : int
    status: str
    method: PaymentMethod
    final_amount : Decimal

    model_config = ConfigDict(from_attributes=True)