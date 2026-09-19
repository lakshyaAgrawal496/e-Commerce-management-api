from pydantic import BaseModel, Field, ConfigDict

class InventoryRequest(BaseModel):
    product_id : int = Field(gt=0)
    quantity : int = Field(gt=0)

class InventoryResponse(BaseModel):
    product_id : int
    product_name : str
    quantity : int

    model_config = ConfigDict(from_attributes=True)