# CRUD для блюд
from app.crud.baseCrud import BaseCRUD
from app.db.models.FoodItem import FoodItem


class FoodItemCrud(BaseCRUD[FoodItem]):
    pass