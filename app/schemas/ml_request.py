"""Schemas for ML recommendation requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field


class MLRecommendationRequest(BaseModel):
    """Request to get ML-based recommendations."""
    
    phone: Optional[str] = Field(None, description="User phone number")
    current_cart: List[str] = Field(
        ..., 
        description="List of dish names currently in cart"
    )
    limit: int = Field(5, ge=1, le=20, description="Max number of recommendations")


class DishRecommendation(BaseModel):
    """Single dish recommendation."""
    
    id: int
    name: str
    category: str
    price_rub: float
    confidence: float = Field(..., ge=0.0, le=1.0)


class MLRecommendationResponse(BaseModel):
    """Response with ML-based recommendations."""
    
    recommendations: List[DishRecommendation]
    source: str = Field(
        ..., 
        description="'ml_model' for ML predictions or 'fallback_rules' for associations"
    )
    user_order_count: Optional[int] = None
    processing_time_ms: float
