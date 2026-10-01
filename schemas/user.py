from database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(10))