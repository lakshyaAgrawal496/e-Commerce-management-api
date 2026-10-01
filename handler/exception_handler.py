from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from models.response import ErrorDetail
from utils.response import error_response
from exceptions import UserAlreadyExistsError,UserNotFoundError,AuthenticationError,AuthorizationError,CartNotFoundError,CartItemNotFoundError,InventoryNotFoundError,InsufficientStockError,OrderNotFoundError,OrderCannotBeCancelledError,OrderCannotBeReturnedError,ReturnAlreadyRequestedError,PaymentFailedError,PaymentRefundError,ProductNotFoundError,AlreadyCancelledOrderError

async def integrity_error_handler(request: Request,exc: IntegrityError):
    return error_response(
        status_code=status.HTTP_409_CONFLICT,
        message="Database integrity constraint violated"
    )

async def user_already_exists(request:Request, exc:UserAlreadyExistsError):
    return error_response(
        status_code=status.HTTP_409_CONFLICT,
        message="User already exists",
        errors=[ErrorDetail(field="email",message="Useremail already registered")]
    )

async def user_not_found(request:Request, exc:UserNotFoundError):
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message="User not found",
        errors=[ErrorDetail(field="user_id",message="User not found")]
    )

async def authentication_handler(request:Request, exc:AuthenticationError):
    return error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=str(exc),
        errors=[ErrorDetail(field="authentication", message=str(exc))]
    )   

async def authorization_handler(request:Request, exc:AuthorizationError):
    return error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        message=str(exc),
        errors=[ErrorDetail(field="role", message=str(exc))]
    )

async def request_validation_handler(request:Request, exc:RequestValidationError):
    errors=[]
    for error in exc.errors():
        field=str(error["loc"][-1])
        errors.append(ErrorDetail(field=field, message=error["msg"]))

    return error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        message="Validation Error",
        errors=errors
    )

async def cart_not_found(request:Request, exc:CartNotFoundError):
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message="Cart not found",
        errors=[ErrorDetail(field="cart_id",message="Cart not exist for this user")]
    )

async def cart_item_not_found(request:Request, exc:CartItemNotFoundError):
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message="Cart item not found",
        errors=[ErrorDetail(field="cart_id , product_id",message="Cart item not found")]
    )

async def inventory_not_found(request:Request, exc:InventoryNotFoundError):
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message="Inventory not found",
        errors=[ErrorDetail(field="product_id",message="Inventory not exist for this product")]
    )

async def insufficient_stock(request:Request, exc:InsufficientStockError):
    return error_response(
        status_code=status.HTTP_409_CONFLICT,
        message="Insufficient stock",
        errors=[ErrorDetail(field="product_id",message="Insufficient stock")]
    )

async def product_not_found(request:Request, exc:ProductNotFoundError):
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message="Product not found",
        errors=[ErrorDetail(field="product_id",message="Product not found")]
    )

async def order_not_found(request:Request, exc:OrderNotFoundError):
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message="Order not found",
        errors=[ErrorDetail(field="order_id",message="Order not found")]
    )

async def order_cannotbe_cancelled(request:Request, exc:OrderCannotBeCancelledError):
    return error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message="Order can not be cancelled as it got shipped/delivered",
        errors=[ErrorDetail(field="order_id",message="Order can not be cancelled")]
    )

async def order_cannotbe_returned(request:Request, exc:OrderCannotBeReturnedError):
    return error_response(
        status_code=status.HTTP_409_CONFLICT,
        message="Order can not be returned before delivery",
        errors=[ErrorDetail(field="order_id",message="Order can not be returned")]
    )

async def return_already_requested(request:Request, exc:ReturnAlreadyRequestedError):
    return error_response(
        status_code=status.HTTP_409_CONFLICT,
        message="Order return already requested",
        errors=[ErrorDetail(field="order_id",message="Order return already requested")]
    )

async def payment_refund(request:Request, exc:PaymentRefundError):
    return error_response(
        status_code=status.HTTP_409_CONFLICT,
        message="Payment refund in process",
        errors=[ErrorDetail(field="order_id",message="Payment return request has been already initiated, it will reflect in your Ac in 3-4 wroking days")]
    )

async def payment_failed(request:Request, exc:PaymentFailedError):
    return error_response(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        message="Payment failed",
        errors=[ErrorDetail(field="order_id",message="Payment failed! Retry again")]
    )

async def order_already_cancelled(request:Request, exc:AlreadyCancelledOrderError):
    return error_response(
        status_code=status.HTTP_409_CONFLICT,
        message="Order already cancelled",
        errors=[ErrorDetail(field="order_id",message="Order already cancelled")]
    )
