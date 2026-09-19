from database import Base
from sqlalchemy import Column, Integer, String, DECIMAL
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100))
    category = Column(String(100))
    description = Column(String(255))
    unit_price = Column(DECIMAL)

    cart_items = relationship("CartItem", back_populates="product")
    inventory = relationship("Inventory",back_populates="product")
    order_items = relationship("OrderItem",back_populates="product")
