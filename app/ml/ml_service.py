"""ML recommendation service with fallback mechanism."""

import time
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.FoodItem import FoodItem
from app.db.models.Order import Order
from app.db.models.User import User
from app.ml.errors import ModelLoadError, PredictionError, InvalidInputError
from app.schemas.ml_request import DishRecommendation

logger = logging.getLogger(__name__)


class MLRecommendationService:
    """Service for ML-based and fallback recommendations (Single Responsibility + DRY)."""
    
    def __init__(self, model_dir: str):
        """Initialize with model directory path. Raises ModelLoadError if model not found."""
        self.model_dir = model_dir
        self._embedding_model: Optional[object] = None
        self._predictor: Optional[object] = None
        self._is_initialized = False
        self._init_failed = False
        
    def _init_model(self) -> None:
        """Lazy load ML model components (only once)."""
        if self._is_initialized or self._init_failed:
            if self._init_failed:
                raise ModelLoadError("ML model initialization previously failed")
            return
        
        try:
            # Lazy imports to avoid hard dependency on ML packages
            from app.ml.embedding import SentenceTransformerEmbedding
            from app.ml.predictor import Predictor
            
            self._embedding_model = SentenceTransformerEmbedding()
            self._predictor = Predictor(self.model_dir, self._embedding_model)
            self._is_initialized = True
            logger.info("ML model initialized successfully")
        except ModuleNotFoundError as e:
            logger.error(f"ML dependencies not installed: {e}")
            self._init_failed = True
            raise ModelLoadError(f"ML dependencies missing: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to initialize ML model: {e}")
            self._init_failed = True
            raise ModelLoadError(f"Cannot load model from {self.model_dir}: {str(e)}")
    
    def get_recommendations(
        self,
        db: Session,
        phone: Optional[str],
        current_cart: List[str],
        limit: int = 5
    ) -> Tuple[List[DishRecommendation], str, Optional[int]]:
        """
        Get recommendations using ML model with fallback to association rules.
        
        Returns: (recommendations, source, user_order_count)
        - source: "ml_model", "fallback_rules", or "hybrid"
        """
        if not current_cart:
            raise InvalidInputError("Current cart cannot be empty")
        
        # Try ML model
        ml_recommendations = []
        user_order_count = None
        source = "fallback_rules"
        
        try:
            self._init_model()
            ml_recommendations, user_order_count = self._predict_ml(
                db, phone, current_cart, limit
            )
            # Убираем проверку "if ml_recommendations" - они уже есть
            source = "ml_model"  # Всегда ставим ml_model, если дошли сюда без ошибок
        except PredictionError as e:
            logger.warning(f"ML prediction failed: {e}, using fallback")
            ml_recommendations = []
            user_order_count = None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            ml_recommendations = []
            user_order_count = None
        
        # If ML didn't return enough recommendations, supplement with association rules
        if len(ml_recommendations) < limit:
            fallback_recommendations = self._get_association_rules(
                db, current_cart, limit - len(ml_recommendations)
            )
            
            # Avoid duplicates by name
            existing_names = {r.name for r in ml_recommendations}
            for rec in fallback_recommendations:
                if rec.name not in existing_names and len(ml_recommendations) < limit:
                    ml_recommendations.append(rec)
                    existing_names.add(rec.name)
            
            # Update source if we added fallback recommendations
            if len(ml_recommendations) > 0 and source != "ml_model":
                source = "fallback_rules"
            elif len(ml_recommendations) > len([r for r in ml_recommendations if r.name in {rec.name for rec in fallback_recommendations}]):
                source = "hybrid"
        
        return ml_recommendations, source, user_order_count
    
    def _predict_ml(
        self,
        db: Session,
        phone: Optional[str],
        current_cart: List[str],
        limit: int
    ) -> Tuple[List[DishRecommendation], Optional[int]]:
        """Execute ML prediction. Raises PredictionError on failure."""
        from app.ml.query_builder import QueryBuilder
        
        
        user = self._get_user(db, phone)
        food_map = self._get_food_map(db)
        
        # Get user history or use new user defaults
        if user:
            prev_orders = self._get_user_order_history(db, user.id)
            total_orders = len(prev_orders) + 1
        else:
            prev_orders = []
            total_orders = 1
        
        # Build query for ML model
        query_dict = QueryBuilder.build(
            prev_orders_items=prev_orders,
            current_items=current_cart,
            dt=datetime.now(),
            total_orders=total_orders
        )
        
        # Get prediction
        try:
            predicted_names = self._predictor.predict(query_dict)
        except Exception as e:
            raise PredictionError(f"Model prediction failed: {str(e)}")
        
        predicted_names = self._predictor.predict(query_dict)
        print("=-" * 70)
        print(f"ML PREDICTED: {predicted_names}")
        print(f"Current cart: {current_cart}")
        print("=-" * 70)

        # Map predictions to dishes
        recommendations = []
        for i, dish_name in enumerate(predicted_names[:limit]):
            food = self._find_food_by_name(food_map, dish_name)
            if food:
                print(f"✓ Found: {dish_name} -> {food.name}")
                # ... добавление
            else:
                print(f"✗ NOT FOUND: {dish_name}")
            food = self._find_food_by_name(food_map, dish_name)
            if food:
                confidence = 1.0 / (i + 1)  # Higher confidence for first predictions
                recommendations.append(
                    DishRecommendation(
                        id=food.id,
                        name=food.name,
                        category=food.category,
                        price_rub=food.price_rub,
                        confidence=round(confidence, 3)
                    )
                )
        
        # If no valid recommendations found from ML, trigger fallback
        if not recommendations:
            raise PredictionError("ML model predicted items not found in current catalog")
        
        return recommendations, total_orders
    
    def _get_association_rules(
        self,
        db: Session,
        current_cart: List[str],
        limit: int
    ) -> List[DishRecommendation]:
        """Get recommendations using association rules (market basket analysis)."""
        try:
            # Import here to avoid circular imports and optional dependency
            from app.api.recommendations import _association_candidates, _food_map
            
            # Get current cart IDs
            food_map = _food_map(db)
            cart_ids = [
                fid for fid, f in food_map.items()
                if f.name in current_cart
            ]
            
            if not cart_ids:
                return self._get_popular_items(db, limit)
            
            # Get association candidates
            candidates = _association_candidates(db, cart_ids, limit)
            
            return [
                DishRecommendation(
                    id=c["id"],
                    name=c["name"],
                    category=c["category"],
                    price_rub=c["price_rub"],
                    confidence=round(c.get("confidence", 0.5), 3)
                )
                for c in candidates[:limit]
            ]
        except Exception as e:
            logger.error(f"Association rules failed: {e}")
            return self._get_popular_items(db, limit)
    
    def _get_popular_items(self, db: Session, limit: int) -> List[DishRecommendation]:
        """Get top popular items as last resort fallback."""
        from sqlalchemy import func
        
        try:
            popular = db.query(
                FoodItem.id,
                FoodItem.name,
                FoodItem.category,
                FoodItem.price_rub,
                func.count(Order.id).label("order_count")
            ).outerjoin(Order, FoodItem.id == Order.food_id).group_by(
                FoodItem.id
            ).order_by(func.count(Order.id).desc()).limit(limit).all()
            
            return [
                DishRecommendation(
                    id=item[0],
                    name=item[1],
                    category=item[2],
                    price_rub=item[3],
                    confidence=0.5
                )
                for item in popular
            ]
        except Exception as e:
            logger.error(f"Failed to get popular items: {e}")
            return []
    
    @staticmethod
    def _get_user(db: Session, phone: Optional[str]) -> Optional[User]:
        """Find user by phone number."""
        if not phone:
            return None
        
        digits = "".join(ch for ch in phone if ch.isdigit())
        if not digits:
            return None
        
        try:
            return db.query(User).filter(User.phone_number == int(digits)).first()
        except Exception as e:
            logger.warning(f"Error finding user: {e}")
            return None
    
    @staticmethod
    def _get_user_order_history(db: Session, user_id: int) -> List[List[str]]:
        """Get user's order history as list of item lists."""
        try:
            orders = db.query(Order).filter(Order.user_id == user_id).all()
            food_map = {f.id: f.name for f in db.query(FoodItem).all()}
            
            order_dict = {}
            for order in orders:
                if order.food_id and order.food_id in food_map:
                    if order.order_id not in order_dict:
                        order_dict[order.order_id] = []
                    order_dict[order.order_id].append(food_map[order.food_id])
            
            return list(order_dict.values())
        except Exception as e:
            logger.warning(f"Error getting order history: {e}")
            return []
    
    @staticmethod
    def _get_food_map(db: Session) -> dict:
        """Get all food items as mapping: id -> FoodItem."""
        try:
            return {food.id: food for food in db.query(FoodItem).all()}
        except Exception as e:
            logger.error(f"Error loading food map: {e}")
            return {}
    
    @staticmethod
    def _find_food_by_name(food_map: dict, name: str) -> Optional[FoodItem]:
        """Find food item by name with synonym mapping."""
    
        # Словарь синонимов (ML название -> реальное название в БД)
        synonyms = {
            'Бургер Биф пита': 'Биф пита',
            'Бургер Биф пита': 'Биф-пита',
            'Филадельфия том-ям': 'Филадельфия том-ям с соусом чимичурри',
            # Добавьте другие синонимы по мере необходимости
        }
        
        # Проверяем синоним
        search_name = synonyms.get(name, name)
        
        name_lower = search_name.lower().strip()
        
        for food in food_map.values():
            food_name_lower = food.name.lower()
            
            # Точное совпадение
            if food_name_lower == name_lower:
                return food
            
            # Частичное совпадение
            if name_lower in food_name_lower or food_name_lower in name_lower:
                return food
        
        # Если не нашли, пробуем оригинальное имя ML
        if search_name != name:
            name_lower = name.lower().strip()
            for food in food_map.values():
                food_name_lower = food.name.lower()
                if name_lower in food_name_lower or food_name_lower in name_lower:
                    return food
        
        return None


class MLRecommendationServiceFactory:
    """Factory for creating and managing ML service singleton."""
    
    _instance: Optional[MLRecommendationService] = None
    
    @classmethod
    def get_service(cls, model_dir: str = "app/ml/rag_order_model_custom") -> MLRecommendationService:
        """Get or create ML service singleton."""
        if cls._instance is None:
            cls._instance = MLRecommendationService(model_dir)
        return cls._instance
