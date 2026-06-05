from fastapi import APIRouter

from app.api import dishes, orders, recommendations, users, front
from app.ml import api as ml_api

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dishes.router, prefix="/dishes", tags=["dishes"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(ml_api.router, prefix="/ml", tags=["ml"])
api_router.include_router(front.front, prefix="", tags=["front"])
