from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from models import UserRequest, UserResponse,Token
from schemas import User
from repositories import AuthRepo
from utils.auth import generate_access_token
from exceptions import UserAlreadyExistsError,UserNotFoundError,AuthenticationError
import logging

logger = logging.getLogger("GrocerEase.auth_service")

class AuthService:
    def __init__(self,db:AsyncSession):
        self.auth_repo = AuthRepo(db)
        self.bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def register(self,user: UserRequest):
        existing_user = await self.auth_repo.get_user(user.email)
        if existing_user:
            logger.warning(f"Registration failed: user already exists - email={user.email}")
            raise UserAlreadyExistsError()

        user_data = User(
            user_name=user.user_name,
            email=user.email,
            password=self.bcrypt_context.hash(user.password),
            role="customer"
        )
        user = await self.auth_repo.create_user(user_data)
        logger.info(f"User registered successfully - user_id={user.user_id}")
        return UserResponse.model_validate(user)
    
    async def login(self, email:str, password:str):
        user = await self.auth_repo.get_user(email)
        if user is None:
            logger.warning(f"Login failed: user not found - email={email}")
            raise UserNotFoundError()

        if not self.bcrypt_context.verify(password, user.password):
            logger.warning(f"Login failed: invalid credentials - email={email}")
            raise AuthenticationError("Invalid login credentials")

        logger.info(f"User logged in successfully - user_id={user.user_id}")
        token = generate_access_token(user.user_id, user.email, user.role)
        return Token(access_token=token, token_type="bearer")
