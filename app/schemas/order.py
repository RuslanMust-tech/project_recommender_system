# здесь будут pydantic модели для заказов, которые будут использоваться в API и для валидации данных
from pydantic import BaseModel, ConfigDict
from typing import Optional

class OrderBase(BaseModel):
    order_id: int
    user_id: int
    food_id: int

# Модель для создания заказа (наследуется от OrderBase)
class OrderCreate(OrderBase):
    pass

# Модель для обновления заказа (все поля опциональны)
class OrderUpdate(BaseModel):
    order_id: Optional[int] = None
    user_id: Optional[int] = None
    food_id: Optional[int] = None

# Модель для ответа (включает ID и поддерживает ORM режим)
class OrderResponse(OrderBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)