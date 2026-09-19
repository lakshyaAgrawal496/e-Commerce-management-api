from typing import Any
from models.response import ErrorDetail, APIResponse
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def error_response(status_code:int, message:str, errors:list[ErrorDetail] | None = None):
    response = APIResponse(
        status_code=status_code,
        message=message,
        data=None,
        errors=errors or []
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response)
    )

def success_response(status_code:int, message:str, data:Any=None):
    response = APIResponse(
        status_code=status_code,
        message=message,
        data=data,
        errors=[]
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response)
    )
