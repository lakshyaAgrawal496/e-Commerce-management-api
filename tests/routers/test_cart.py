import unittest
from unittest.mock import AsyncMock, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers import cart_router
from dependencies import get_db
from utils.auth import get_current_user
from exceptions.cart_exceptions import CartItemNotFoundError, CartNotFoundError
from handler.exception_handler import cart_item_not_found, cart_not_found
from models import CartItemResponse, CartResponse

class TestCartRouter(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(cart_router.router)
        self.cart_service = AsyncMock()
        self.client = TestClient(self.app)
        self.app.dependency_overrides[get_db] = lambda: None
        self.user = {
            "user_id": 1,
            "email": "lakshya@mail.com",
            "role": "customer"
        }
        self.app.dependency_overrides[get_current_user] = lambda: self.user
        cart_router.CartService = Mock(return_value=self.cart_service)
        self.app.add_exception_handler(CartNotFoundError,cart_not_found)
        self.app.add_exception_handler(CartItemNotFoundError,cart_item_not_found)

    def test_add_to_cart(self):
        self.cart_service.add_to_cart.return_value = CartResponse(
            cart_id=1,
            items=[CartItemResponse(product_id=1,product_name="Laptop",unit_price=100000,quantity=2)
            ]
        )
        response = self.client.post("/cart",json={"product_id": 1,"quantity": 2})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"],"Product Added to cart successfully")

    def test_get_cart(self):
        self.cart_service.get_cart.return_value = CartResponse(
            cart_id=1,
            items=[CartItemResponse(product_id=1,product_name="Laptop",unit_price=100000,quantity=2)
            ]
        )
        response = self.client.get("/cart")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"],"Cart fetched successfully")

    def test_remove_from_cart(self):
        self.cart_service.remove_from_cart.return_value = None
        response = self.client.delete("/cart/item/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"],"Cart deleted successfully")

    def test_remove_from_cart_invalid_product_id(self):
        response = self.client.delete("/cart/item/0")

        self.assertEqual(response.status_code, 422)

    def test_remove_from_cart_cart_not_found(self):
        self.cart_service.remove_from_cart.side_effect = CartNotFoundError()
        response = self.client.delete("/cart/item/100")

        self.assertEqual(response.status_code, 404)

    def test_remove_from_cart_item_not_found(self):
        self.cart_service.remove_from_cart.side_effect = CartItemNotFoundError()
        response = self.client.delete("/cart/item/100")

        self.assertEqual(response.status_code, 404)

    