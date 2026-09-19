from fastapi import Depends
from typing import Annotated
from jose import jwt, JWTError
from constants import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta, timezone
from dependencies import token_dependency
from exceptions.auth_exceptions import (AuthorizationError,AuthenticationError)

def generate_access_token(user_id:int, email:str, role:str):
        expires = datetime.now(timezone.utc)+timedelta(minutes=20)
        payload = {
            "sub" : str(user_id),
            "email" : email,
            "role" : role,
            "exp" : expires
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: token_dependency):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")

        if user_id is None or email is None or role is None:
            raise AuthenticationError("Invalid credentials")
        return {
            "user_id" : int(user_id),
            "email" : email,
            "role" : role
        }
    except JWTError:
        raise AuthenticationError("Invalid or expired token")
     
user_dependency = Annotated[dict,Depends(get_current_user)]

def get_admin_auth(current_user: user_dependency):
    if current_user["role"] != "admin":
        raise AuthorizationError("Customers not authorized")
    return current_user

admin_dependency = Annotated[dict,Depends(get_admin_auth)]
     