from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from utils.enums import PaymentMethod

class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer,primary_key=True,autoincrement=True)
    order_id = Column(Integer,ForeignKey("orders.order_id"),unique=True)
    status = Column(String(20))
    method = Column(Enum(PaymentMethod))
    final_amount = Column(DECIMAL(10,2))

    order = relationship("Order",back_populates="payment")

