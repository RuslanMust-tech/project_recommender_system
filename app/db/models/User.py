from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'  # точно как в вашем запросе
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(Integer, nullable=False)
    
    # Связь с заказами (опционально, для удобства)
    orders = relationship("Order", back_populates="user")


