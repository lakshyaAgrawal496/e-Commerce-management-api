from database import Base
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime, Enum
from utils.enums import OrderStatus
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    total_amount = Column(DECIMAL(10,2))
    discount_amount = Column(DECIMAL(10,2))
    final_amount = Column(DECIMAL(10,2))
    status = Column(Enum(OrderStatus))
    ordered_at = Column(DateTime, default=lambda:datetime.now(timezone.utc))

    items = relationship("OrderItem",back_populates="order")
    return_orders = relationship("ReturnOrder",back_populates="order")
    payment = relationship("Payment",back_populates="order",uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    product_id = Column(Integer,ForeignKey("products.product_id"))
    quantity = Column(Integer)

    order = relationship("Order",back_populates="items")
    product = relationship("Product",back_populates="order_items")

class ReturnOrder(Base):
    __tablename__ = "return_orders"
    return_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    reason = Column(String(255))

    order = relationship("Order",back_populates="return_orders")
