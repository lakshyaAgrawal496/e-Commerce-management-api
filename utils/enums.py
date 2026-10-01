from enum import Enum

class OrderStatus(str, Enum):
    PLACED = "PLACED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"

class OrderUpdateStatus(str,Enum):
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"

class PaymentMethod(str,Enum):
    CARD = "CARD"
    COD = "COD"
    UPI = "UPI"

class PaymentStatus(str,Enum):
    PENDING = "PENDING"      
    SUCCESS = "SUCCESS"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"