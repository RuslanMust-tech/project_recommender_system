from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base

class Order(Base):
    __tablename__ = "Order"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("User.id"))
    food_id = Column(Integer, ForeignKey("food_catalog.id"))

    user = relationship("User", back_populates="orders")
    food_item = relationship("FoodItem", back_populates="orders")
