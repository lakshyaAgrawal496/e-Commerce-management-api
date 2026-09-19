from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal

class ProductRequest(BaseModel):
    product_name : str = Field(min_length=3)
    category : str = Field(min_length=3)
    description : str = Field(min_length=10)
    unit_price : Decimal = Field(gt=0)

    @field_validator("product_name","category","description")
    @classmethod
    def validate_strings(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Field cannot contain only whitespace")
        return value

class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    category: str
    description: str
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)