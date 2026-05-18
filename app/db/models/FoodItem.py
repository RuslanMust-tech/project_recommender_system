from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import Session

from sqlalchemy import create_engine

Base = declarative_base()

class FoodItem(Base):
    __tablename__ = 'food_catalog'
    
    # Schema
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    pieces = Column(Integer)
    weight_g = Column(Integer)
    composition = Column(JSON)  # Храним список ингредиентов
    proteins_g = Column(Float)
    fats_g = Column(Float)
    carbs_g = Column(Float)
    calories_kcal = Column(Integer)
    price_rub = Column(Integer)

    def save_to_db(self, session: Session):
        """Сохранить в БД"""
        session.add(self)
        session.commit()
        return self.id
    


