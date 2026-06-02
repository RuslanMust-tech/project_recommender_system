# здесь будут pydantic модели для блюд, которые будут использоваться в API и для валидации данных
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from decimal import Decimal

class FoodItemBase(BaseModel):
    """Базовые поля блюда"""
    category: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    pieces: Optional[int] = Field(None, ge=0)
    weight_g: Optional[int] = Field(None, ge=0)
    composition: Optional[List[str]] = Field(None, )
    proteins_g: Optional[float] = Field(None, ge=0)
    fats_g: Optional[float] = Field(None, ge=0, )
    carbs_g: Optional[float] = Field(None, ge=0)
    calories_kcal: Optional[int] = Field(None, ge=0)
    price_rub: int = Field(..., gt=0)
    model_config = ConfigDict(from_attributes=True)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Название не может быть пустым')
        return v.strip()
    
class FoodItemUpdate(FoodItemBase):
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    pieces: Optional[int] = Field(None, ge=0)
    weight_g: Optional[int] = Field(None, ge=0)
    composition: Optional[List[str]] = None
    proteins_g: Optional[float] = Field(None, ge=0)
    fats_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    calories_kcal: Optional[int] = Field(None, ge=0)
    price_rub: Optional[int] = Field(None, gt=0)

class FoodItemResponse(FoodItemBase):
    pass

class FoodItemSearch(BaseModel):
    id: int = Field(None)
    category: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    
    name_like: Optional[str] = Field(None)
    
    price_min: Optional[int] = Field(None, ge=0)
    price_max: Optional[int] = Field(None, ge=0)
    
    calories_min: Optional[int] = Field(None, ge=0)
    calories_max: Optional[int] = Field(None, ge=0)
    
    weight_min: Optional[int] = Field(None, ge=0)
    weight_max: Optional[int] = Field(None, ge=0)
    
    # Сортировка
    sort_by: Optional[str] = Field(
        None, 
        description="Поле для сортировки (price_rub, calories_kcal, name)",
        pattern="^(price_rub|calories_kcal|name)$"
    )
    sort_order: Optional[str] = Field(
        "asc", 
        description="Порядок сортировки (asc/desc)",
        pattern="^(asc|desc)$"
    )
    
    # Пагинация
    limit: Optional[int] = Field(50, ge=1, le=100, description="Количество записей")
    offset: Optional[int] = Field(0, ge=0, description="Пропустить записей")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "Фрукты",
                "name_like": "яб",
                "price_min": 50,
                "price_max": 150,
                "calories_max": 100,
                "sort_by": "price_rub",
                "sort_order": "asc",
                "limit": 20
            }
        }

        