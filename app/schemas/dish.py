# здесь будут pydantic модели для блюд, которые будут использоваться в API и для валидации данных
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal

class FoodItemBase(BaseModel):
    """Базовые поля блюда"""
    category: str = Field(..., min_length=1, max_length=50, description="Категория блюда")
    name: str = Field(..., min_length=1, max_length=100, description="Название блюда")
    pieces: Optional[int] = Field(None, ge=0, description="Количество штук")
    weight_g: Optional[int] = Field(None, ge=0, description="Вес в граммах")
    composition: Optional[List[str]] = Field(None, description="Состав блюда (JSON)")
    proteins_g: Optional[float] = Field(None, ge=0, description="Белки в граммах")
    fats_g: Optional[float] = Field(None, ge=0, description="Жиры в граммах")
    carbs_g: Optional[float] = Field(None, ge=0)
    calories_kcal: Optional[int] = Field(None, ge=0)
    price_rub: int = Field(..., gt=0)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Название не может быть пустым')
        return v.strip()


class FoodItemSearch(BaseModel):
    """Универсальная схема поиска"""
    # Точные совпадения
    category: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    
    # Частичное совпадение
    name_like: Optional[str] = Field(None)
    
    # Диапазоны
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