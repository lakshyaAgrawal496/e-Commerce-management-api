import unittest
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers import order_router
from dependencies import get_db
from utils.auth import get_current_user
from models import OrderResponse, OrderItemResponse
from utils.enums import PaymentMethod, OrderStatus
from exceptions import OrderNotFoundError,OrderCannotBeCancelledError,OrderCannotBeReturnedError,AlreadyCancelledOrderError
from handler.exception_handler import order_already_cancelled, order_cannotbe_cancelled, order_cannotbe_returned,order_not_found

class TestOrderRouter(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(order_router.router)
        self.order_service = AsyncMock()
        self.client = TestClient(self.app)
        self.app.dependency_overrides[get_db] = lambda: None
        self.user = {
            "user_id": 1,
            "email": "lakshya@gmail.com",
            "role": "customer"
        }
        self.app.dependency_overrides[get_current_user] = (lambda: self.user)
        order_router.OrderService = Mock(return_value=self.order_service)
        self.app.add_exception_handler(OrderNotFoundError,order_not_found)
        self.app.add_exception_handler(AlreadyCancelledOrderError,order_already_cancelled)
        self.app.add_exception_handler(OrderCannotBeCancelledError,order_cannotbe_cancelled)
        self.app.add_exception_handler(OrderCannotBeReturnedError,order_cannotbe_returned)

    def get_order_response(self):
        return OrderResponse(
            user_id=1,
            ordered_at=datetime.now(timezone.utc),
            order_id=1,
            payment_id=1,
            order_status=OrderStatus.PLACED,
            total_amount=Decimal("1000"),
            discounted_amount=Decimal("100"),
            final_amount=Decimal("900"),
            items=[OrderItemResponse(product_id=1,product_name="Laptop",unit_price=Decimal("1000"),quantity=1)
            ]
        )

    def test_place_order(self):
        self.order_service.place_order.return_value = (self.get_order_response())
        response = self.client.post("/order/place",params={"method": PaymentMethod.COD.value})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"],"Order placed successfully")

    def test_get_order_history(self):
        self.order_service.get_order_history.return_value = [self.get_order_response()]
        response = self.client.get("/order/history")

        self.assertEqual(response.status_code, 200)

    def test_get_order_by_id(self):
        self.order_service.get_order.return_value = (self.get_order_response())
        response = self.client.get("/order/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"],"Order fetched successfully")

    def test_cancel_order(self):
        self.order_service.cancel_order.return_value = (self.get_order_response())
        response = self.client.patch("/order/cancel/1")

        self.assertEqual(response.status_code, 200)

    def test_return_order(self):
        self.order_service.return_order.return_value = (self.get_order_response())
        response = self.client.post("/order/return/1",params={"reason": "Product damaged"})

        self.assertEqual(response.status_code, 200)

    def test_get_order_invalid_id(self):
        response = self.client.get("/order/0")
        self.assertEqual(response.status_code, 422)

    def test_get_order_not_found(self):
        self.order_service.get_order.side_effect = OrderNotFoundError()
        response = self.client.get("/order/999")

        self.assertEqual(response.status_code, 404)

    def test_get_order_history_not_found(self):
        self.order_service.get_order_history.side_effect =  OrderNotFoundError()
        response = self.client.get("/order/history")

        self.assertEqual(response.status_code, 404)

    def test_cancel_already_cancelled(self):
        self.order_service.cancel_order.side_effect = AlreadyCancelledOrderError()
        response = self.client.patch("/order/cancel/1")

        self.assertEqual(response.status_code, 402)

    