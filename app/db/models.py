# Здесь будут находиться модели для ORM SQLAlchemy

# from datetime import datetime

# from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
# from sqlalchemy.orm import relationship

# from app.db.session import Base


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String(255), unique=True, nullable=False, index=True)
#     name = Column(String(120), nullable=False)
#     role = Column(String(50), nullable=False, default="customer")
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

#     orders = relationship("Order", back_populates="user")


# class Restaurant(Base):
#     __tablename__ = "restaurants"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(200), nullable=False)
#     location = Column(String(255), nullable=True)
#     rating = Column(Float, nullable=True)

#     dishes = relationship("Dish", back_populates="restaurant")


# class Dish(Base):
#     __tablename__ = "dishes"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(200), nullable=False)
#     description = Column(Text, nullable=True)
#     price = Column(Float, nullable=False)
#     category = Column(String(100), nullable=True)
#     restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)

#     restaurant = relationship("Restaurant", back_populates="dishes")
#     order_items = relationship("OrderItem", back_populates="dish")


# class Order(Base):
#     __tablename__ = "orders"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     status = Column(String(50), nullable=False, default="created")
#     total_amount = Column(Float, nullable=False, default=0.0)
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

#     user = relationship("User", back_populates="orders")
#     items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


# class OrderItem(Base):
#     __tablename__ = "order_items"

#     id = Column(Integer, primary_key=True, index=True)
#     order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
#     dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
#     quantity = Column(Integer, nullable=False, default=1)
#     unit_price = Column(Float, nullable=False)

#     order = relationship("Order", back_populates="items")
#     dish = relationship("Dish", back_populates="order_items")
