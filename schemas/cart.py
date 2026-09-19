from database import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class Cart(Base):
    __tablename__ = "carts"
    cart_id = Column(Integer,primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.user_id"))

    items = relationship("CartItem", back_populates="cart", cascade="delete")

class CartItem(Base):
    __tablename__ = "cart_items"
    cart_item_id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer,ForeignKey("carts.cart_id"))
    product_id = Column(Integer,ForeignKey("products.product_id"))
    quantity = Column(Integer)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
