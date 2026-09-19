import json
import unittest
from unittest import TestCase
from unittest.mock import AsyncMock, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers import auth_router
from models import UserResponse, Token
from exceptions import UserAlreadyExistsError, UserNotFoundError, AuthenticationError
from handler.exception_handler import user_not_found, user_already_exists, authentication_handler
from database import get_db

class TestAuthRouter(TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(auth_router.router)
        self.auth_service = AsyncMock()
        self.client = TestClient(self.app)
        self.app.dependency_overrides[get_db] = lambda: None
        auth_router.AuthService = Mock(return_value=self.auth_service)
        self.app.add_exception_handler(UserNotFoundError,user_not_found)
        self.app.add_exception_handler(UserAlreadyExistsError,user_already_exists)
        self.app.add_exception_handler(AuthenticationError,authentication_handler)

    def test_register(self):
        result = UserResponse(
            user_id=1,
            user_name="Lakshya",
            email="lakshya@mail.com",
            role="customer"
        )
        self.auth_service.register.return_value = result
        response = self.client.post("/auth/register",json={"user_name": "Lakshya","email": "lakshya@mail.com","password": "1234"})

        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json()["message"],"User registered successfully")

    def test_login(self):
        result = Token(
            access_token="abcd",
            token_type="bearer"
        )
        self.auth_service.login.return_value = result
        response = self.client.post("/auth/login",data={"username":"Lakshya","password":"1234"})

        self.assertEqual(response.status_code,200)

    def test_login_user_not_found(self):
        self.auth_service.login.side_effect = UserNotFoundError()
        response = self.client.post("/auth/login",data={"username":"abcd","password":"xyz"})

        self.assertEqual(response.status_code,404)

    def test_login_invalid_password(self):
        self.auth_service.login.side_effect = AuthenticationError("Invalid login credentials")
        response = self.client.post("/auth/login",data={"username": "lakshya@mail.com","password": "wrong"})

        self.assertEqual(response.status_code,401)

    def test_register_user_already_exists(self):
        self.auth_service.register.side_effect = UserAlreadyExistsError()
        response = self.client.post("/auth/register",json={"user_name":"Lakshya","email":"lakshya@mail.com","password":"1234"})

        self.assertEqual(response.status_code,409)

    def test_register_validation(self):
        response = self.client.post("/auth/register",json={"user_name":" ","email":"abcd","password":""})

        self.assertEqual(response.status_code,422)