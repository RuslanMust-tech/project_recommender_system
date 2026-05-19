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

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed_categories = ['Роллы', 'main', 'salad', 'drink', 'dessert']
        if v not in allowed_categories:
            raise ValueError(f'Категория должна быть одной из: {allowed_categories}')
        return v