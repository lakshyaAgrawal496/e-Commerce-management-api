import unittest
from unittest.mock import AsyncMock, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers import product_router
from dependencies import get_db
from utils.auth import get_current_user
from models import ProductResponse
from exceptions import ProductNotFoundError
from handler.exception_handler import product_not_found

class TestProductRouter(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(product_router.router)
        self.product_service = AsyncMock()
        self.client = TestClient(self.app)
        self.app.dependency_overrides[get_db] = lambda: None
        self.user = {
            "user_id": 1,
            "email": "lakshya@mail.com",
            "role": "customer"
        }
        self.app.dependency_overrides[get_current_user] = lambda: self.user
        product_router.ProductService = Mock(return_value=self.product_service)
        self.app.add_exception_handler(ProductNotFoundError,product_not_found)

    def test_get_product_by_search_term(self):
        self.product_service.get_product_by_search_term.return_value = [
            ProductResponse(product_id=1,product_name="Laptop",category="Electronics",description="Gaming laptop",unit_price=100000),
            ProductResponse(product_id=2,product_name="Laptop Bag",category="Accessories",description="Laptop bag",unit_price=900)
        ]
        response = self.client.get("/product/search",params={"search_term": "Laptop"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"],"Products fetched successfully")

    def test_get_product_by_id(self):
        self.product_service.get_product_by_id.return_value = ProductResponse(product_id=1,product_name="Laptop",category="Electronics",description="Gaming laptop",unit_price=50000)
        response = self.client.get("/product/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"],"Product fetched successfully")

    def test_search_product_validation(self):
        response = self.client.get("/product/search",params={"search_term": ""})
        self.assertEqual(response.status_code, 422)

    def test_get_product_negative_id(self):
        response = self.client.get("/product/-1")
        self.assertEqual(response.status_code, 422)

    def test_search_product_not_found(self):
        self.product_service.get_product_by_search_term.side_effect = ProductNotFoundError()
        response = self.client.get("/product/search",params={"search_term": "xyz"})

        self.assertEqual(response.status_code, 404)

    