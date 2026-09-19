import unittest
from unittest.mock import AsyncMock, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers import inventory_router
from dependencies import get_db
from utils.auth import get_current_user
from models import InventoryResponse
from exceptions import InventoryNotFoundError,ProductNotFoundError
from handler.exception_handler import inventory_not_found, product_not_found

class TestInventoryRouter(unittest.TestCase):

    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(inventory_router.router)
        self.inventory_service = AsyncMock()
        self.client = TestClient(self.app)
        self.app.dependency_overrides[get_db] = lambda: None
        self.user = {
            "user_id": 1,
            "email": "lakshya@gmail.com",
            "role": "customer"
        }
        self.app.dependency_overrides[get_current_user] = lambda: self.user
        inventory_router.InventoryService = Mock(return_value=self.inventory_service)
        self.app.add_exception_handler(InventoryNotFoundError,inventory_not_found)
        self.app.add_exception_handler(ProductNotFoundError,product_not_found)

    def test_get_all_inventory(self):
        self.inventory_service.get_all_inventory.return_value = [
            InventoryResponse(product_id=1,product_name="Laptop",quantity=50),
            InventoryResponse(product_id=2,product_name="Mouse",quantity=100)
        ]
        response = self.client.get("/inventory")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"],"Inventory fetched successfully")

    def test_get_inventory(self):
        self.inventory_service.get_inventory.return_value = InventoryResponse(product_id=1,product_name="Laptop",quantity=50)
        response = self.client.get("/inventory/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"],"Inventory fetched successfully")

    def test_get_inventory_invalid_product_id(self):
        response = self.client.get("/inventory/0")
        self.assertEqual(response.status_code, 422)

    def test_get_inventory_not_found(self):
        self.inventory_service.get_inventory.side_effect = InventoryNotFoundError()
        response = self.client.get("/inventory/999")

        self.assertEqual(response.status_code, 404)
    
    def test_get_all_inventory_not_found(self):
        self.inventory_service.get_all_inventory.side_effect = InventoryNotFoundError()
        response = self.client.get("/inventory")

        self.assertEqual(response.status_code, 404)