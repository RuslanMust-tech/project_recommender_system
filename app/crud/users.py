# CRUD для пользователей
from app.crud.baseCrud import BaseCRUD
from app.db.models import User


class UserCrud(BaseCRUD[User]):
    pass