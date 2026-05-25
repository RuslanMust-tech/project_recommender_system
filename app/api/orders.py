# реализация эндпоинтов для блюд 
from fastapi import Depends
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.crud.orders import OrderCrud
from app.db.models.Order import Order
from app.schemas.order import OrderBase, OrderUpdate, OrderResponse
from app.api.baseRouter import BaseRouter

# Создаем роутер для блюд
class OrdersRouter(BaseRouter[OrderCrud, Order, OrderBase, OrderUpdate, OrderResponse]):
    def _setup_custom_routes(self):
        pass

# Создаем экземпляр роутера
orders_router_instance = OrdersRouter(
    model_class=Order,
    crud_class=OrderCrud,
    create_schema=OrderBase,
    update_schema=OrderUpdate,
    response_schema=OrderResponse,
    response_model=None  # или можно указать свою модель ответа
)
orders_router_instance._setup_custom_routes()
router = orders_router_instance.get_router()