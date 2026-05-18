from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base

class User(Base):
    __tablename__ = "User"
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(Integer, nullable=False)

    orders = relationship("Order", back_populates="user")

