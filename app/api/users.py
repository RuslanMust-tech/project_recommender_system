# реализация эндпоинтов для блюд 
from fastapi import Depends, Request
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.crud.users import UserCrud
from app.db.models.User import User
from app.schemas.user import UserBase, UserUpdate, UserResponse
from app.api.baseRouter import BaseRouter

# Создаем роутер для блюд
class UsersRouter(BaseRouter[UserCrud, User, UserBase, UserUpdate, UserResponse]):
    def _setup_custom_routes(self):
        @self.router.get("/search", response_model=List[self.response_model])
        async def search_by_phone(
            phone_number: int, db: Session = Depends(get_db), request: Request = None):
            print(f"пизда")
            crud = self.crud_class(db, self.model_class)
            items = crud.read_filter(phone_number=phone_number)
            return [self.response_schema.model_validate(item) for item in items]
# Создаем экземпляр роутера
Users_router_instance = UsersRouter(
    model_class=User,
    crud_class=UserCrud,
    create_schema=UserBase,
    update_schema=UserUpdate,
    response_schema=UserResponse,
    response_model=None  # или можно указать свою модель ответа
)
Users_router_instance._setup_custom_routes()
router = Users_router_instance.get_router()