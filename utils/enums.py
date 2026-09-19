from enum import Enum

class OrderStatus(str, Enum):
    PLACED = "PLACED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"

class PaymentMethod(str,Enum):
    CARD = "CARD"
    COD = "COD"
    UPI = "UPI"