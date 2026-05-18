from sqlalchemy import create_engine
from sqladmin import Admin, ModelView

from app.core.config import get_settings
from app.db.models import FoodItem, Order, User

settings = get_settings()
engine = create_engine(settings.database_url, echo=False)


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_list = [User.id, User.phone_number]
    column_sortable_list = [User.id, User.phone_number]
    column_searchable_list = [User.phone_number]


class OrderAdmin(ModelView, model=Order):
    name = "Заказ"
    name_plural = "Заказы"
    column_list = [Order.id, Order.order_id, Order.user_id, Order.food_id]
    column_sortable_list = [Order.id, Order.order_id, Order.user_id, Order.food_id]
    column_searchable_list = [Order.order_id]


class FoodItemAdmin(ModelView, model=FoodItem):
    name = "Блюдо"
    name_plural = "Блюда"
    column_list = [
        FoodItem.id,
        FoodItem.category,
        FoodItem.name,
        FoodItem.price_rub,
        FoodItem.calories_kcal,
    ]
    column_sortable_list = [FoodItem.id, FoodItem.category, FoodItem.name, FoodItem.price_rub]
    column_searchable_list = [FoodItem.category, FoodItem.name]


def setup_admin(app) -> None:
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(FoodItemAdmin)
