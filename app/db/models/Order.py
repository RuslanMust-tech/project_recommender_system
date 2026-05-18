from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import Session

from sqlalchemy import create_engine

Base = declarative_base()

class Order(Base):
    __tablename__ = 'Order'  # точно как в вашем запросе
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('User.id'))
    food_id = Column(Integer, ForeignKey('Food_catalog.id'))
    
    # Связи (опционально, для удобства работы)
    user = relationship("User", back_populates="orders")
    food_item = relationship("Food_catalog", back_populates="orders")