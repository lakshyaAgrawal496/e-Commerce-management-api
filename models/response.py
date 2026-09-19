from pydantic import BaseModel, Field
from typing import Any

class ErrorDetail(BaseModel):
    field : str | None = None
    message : str

class APIResponse(BaseModel):
    status_code : int
    message : str
    data : Any = None
    errors : list[ErrorDetail] = Field(default_factory=list)