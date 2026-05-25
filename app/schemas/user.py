# здесь будут pydantic модели для пользователей, которые будут использоваться в API и для валидации данных
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class UserBase(BaseModel):
    phone_number: int

# Модель для создания пользователя
class UserCreate(UserBase):
    pass

# Модель для обновления пользователя
class UserUpdate(BaseModel):
    phone_number: Optional[int] = None

# Модель для ответа (базовая, без связей)
class UserResponse(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
