# CRUD для заказов
from app.crud.baseCrud import BaseCRUD
from app.db.models import Order


class OrderCrud(BaseCRUD[Order]):
    pass