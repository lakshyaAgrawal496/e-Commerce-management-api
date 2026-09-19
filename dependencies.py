from typing import Annotated
from fastapi import Depends
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

db_dependency = Annotated[AsyncSession,Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

token_dependency = Annotated[str,Depends(oauth2_scheme)]

login_form_dependency = Annotated[OAuth2PasswordRequestForm,Depends()]


