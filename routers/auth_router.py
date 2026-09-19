from fastapi import APIRouter, status
from dependencies import db_dependency, login_form_dependency
from models.user import UserRequest
from models.token import Token
from services import AuthService
from utils.response import success_response

router = APIRouter(
    prefix = "/auth",
    tags = ["Authentication"]
)

@router.post("/register")
async def register(user_data:UserRequest, db:db_dependency):
    auth_service = AuthService(db)
    user = await auth_service.register(user_data)
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=user
    )

@router.post("/login",response_model=Token)
async def login(form_data:login_form_dependency, db:db_dependency):
    auth_service = AuthService(db)
    return await auth_service.login(form_data.username, form_data.password)

