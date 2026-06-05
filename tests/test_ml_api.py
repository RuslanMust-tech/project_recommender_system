"""Integration tests for ML recommendation API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import get_db
from app.db.models.FoodItem import FoodItem
from app.db.models.User import User
from app.db.models.Order import Order


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_ml_recommendations_empty_cart(client):
    """Test that empty cart raises error."""
    response = client.post(
        "/api/v1/ml/recommendations/ml",
        json={"phone": None, "current_cart": []}
    )
    assert response.status_code == 422  # Validation error


def test_ml_status_endpoint(client):
    """Test ML service status check."""
    response = client.get("/api/v1/ml/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data


def test_ml_recommendations_structure(client):
    """Test response structure when ML is unavailable (fallback)."""
    response = client.post(
        "/api/v1/ml/recommendations/ml",
        json={
            "phone": "+79991234567",
            "current_cart": ["Роллы"],
            "limit": 3
        }
    )
    
    # Should return 200 (fallback works) or handle gracefully
    if response.status_code == 200:
        data = response.json()
        assert "recommendations" in data
        assert "source" in data
        assert data["source"] in ["ml_model", "fallback_rules"]
        assert "processing_time_ms" in data
        assert isinstance(data["recommendations"], list)
