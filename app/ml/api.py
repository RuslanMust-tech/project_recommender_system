"""ML recommendation API endpoints."""

import time
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ml.ml_service import MLRecommendationServiceFactory
from app.schemas.ml_request import MLRecommendationRequest, MLRecommendationResponse
from app.ml.errors import InvalidInputError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/recommendations/ml", response_model=MLRecommendationResponse)
async def get_ml_recommendations(
    request: MLRecommendationRequest,
    db: Session = Depends(get_db)
) -> MLRecommendationResponse:
    """
    Get ML-based product recommendations based on user history and current cart.
    
    - **phone**: User phone number (optional, for personalized recommendations)
    - **current_cart**: List of dish names currently in cart
    - **limit**: Maximum number of recommendations (1-20, default 5)
    
    If ML model fails, returns recommendations using association rules (market basket).
    """
    start_time = time.time()
    
    try:
        service = MLRecommendationServiceFactory.get_service()
        
        recommendations, source, user_order_count = service.get_recommendations(
            db=db,
            phone=request.phone,
            current_cart=request.current_cart,
            limit=request.limit
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return MLRecommendationResponse(
            recommendations=recommendations,
            source=source,
            user_order_count=user_order_count,
            processing_time_ms=round(processing_time_ms, 2)
        )
    
    except InvalidInputError as e:
        logger.warning(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ML recommendations: {e}")
        raise


@router.get("/status")
async def ml_service_status() -> dict:
    """Check ML service availability and model status."""
    try:
        service = MLRecommendationServiceFactory.get_service()
        # Try to access model (lazy init if not done)
        service._init_model()
        return {"status": "ok", "model_loaded": service._is_initialized}
    except Exception as e:
        logger.warning(f"ML service status check failed: {e}")
        return {"status": "degraded", "model_loaded": False, "error": str(e)}
