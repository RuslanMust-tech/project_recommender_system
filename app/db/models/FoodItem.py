from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

from app.db.base import Base

class FoodItem(Base):
    __tablename__ = "food_catalog"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    pieces = Column(Integer)
    weight_g = Column(Integer)
    composition = Column(JSON)
    proteins_g = Column(Float)
    fats_g = Column(Float)
    carbs_g = Column(Float)
    calories_kcal = Column(Integer)
    price_rub = Column(Integer)

    orders = relationship("Order", back_populates="food_item")

    def save_to_db(self, session: Session):
        """Сохранить в БД"""
        session.add(self)
        session.commit()
        return self.id
    

