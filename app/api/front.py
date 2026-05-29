from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from datetime import datetime
import random

# Создаём роутер с именем "front" для использования в api_router
front = APIRouter()

# Временная БД (лучше перенести в отдельный модуль)
users_db = {}

# Модели
class CartItem(BaseModel):
    name: str
    price: int
    qty: int
    img: str = ""
    weight: str = ""

class Order(BaseModel):
    id: int
    date: str
    total: int
    payment: str
    address: str
    items: List[str]

class CartRequest(BaseModel):
    phone: str
    cart: List[CartItem]

class OrderRequest(BaseModel):
    phone: str
    order: Order

# ======================
# USER
# ======================

@front.get("/user/{phone}")
def get_user(phone: str):
    """Получить информацию о пользователе"""
    if phone not in users_db:
        users_db[phone] = {
            "phone": phone,
            "cart": [],
            "orders": []
        }
    return users_db[phone]

# ======================
# CART
# ======================

@front.get("/cart/{phone}")
def get_cart(phone: str):
    """Получить корзину пользователя"""
    user = users_db.get(phone)
    if not user:
        return {"cart": []}
    return {"cart": user["cart"]}

@front.post("/cart")
def save_cart(data: CartRequest):
    """Сохранить корзину пользователя"""
    if data.phone not in users_db:
        users_db[data.phone] = {
            "phone": data.phone,
            "cart": [],
            "orders": []
        }
    users_db[data.phone]["cart"] = [item.dict() for item in data.cart]
    return {"message": "Корзина сохранена"}

@front.delete("/cart/{phone}")
def clear_cart(phone: str):
    """Очистить корзину пользователя"""
    if phone in users_db:
        users_db[phone]["cart"] = []
        return {"message": "Корзина очищена"}
    return {"message": "Пользователь не найден"}

# ======================
# ORDERS
# ======================

@front.get("/orders/{phone}")
def get_orders(phone: str):
    """Получить все заказы пользователя"""
    user = users_db.get(phone)
    if not user:
        return {"orders": []}
    return {"orders": user["orders"]}

@front.post("/order")
def create_order(data: OrderRequest):
    """Создать новый заказ"""
    if data.phone not in users_db:
        users_db[data.phone] = {
            "phone": data.phone,
            "cart": [],
            "orders": []
        }
    
    # Генерируем ID для заказа, если его нет
    if not hasattr(data.order, 'id') or data.order.id == 0:
        order_dict = data.order.dict()
        order_dict['id'] = len(users_db[data.phone]["orders"]) + 1
        users_db[data.phone]["orders"].append(order_dict)
    else:
        users_db[data.phone]["orders"].append(data.order.dict())
    
    # Очищаем корзину после оформления заказа
    users_db[data.phone]["cart"] = []
    
    return {"message": "Заказ оформлен", "order_id": users_db[data.phone]["orders"][-1]["id"]}

@front.get("/order/{phone}/{order_id}")
def get_order(phone: str, order_id: int):
    """Получить конкретный заказ"""
    user = users_db.get(phone)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    for order in user["orders"]:
        if order["id"] == order_id:
            return order
    
    raise HTTPException(status_code=404, detail="Заказ не найден")

# ======================
# STATS & UTILS
# ======================

@front.get("/stats")
def get_stats():
    """Получить статистику приложения"""
    total_users = len(users_db)
    total_orders = sum(len(user["orders"]) for user in users_db.values())
    total_items_in_carts = sum(len(user["cart"]) for user in users_db.values())
    
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_items_in_carts": total_items_in_carts
    }

@front.get("/health")
def health_check():
    """Проверка работоспособности"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}