#!/usr/bin/env python3
"""Quick test script for ML recommendation API."""

import sys
import requests
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_api(base_url: str = "http://localhost:8000"):
    """Test ML recommendation endpoints."""
    
    print("=" * 60)
    print("ML Recommendation API Test")
    print("=" * 60)
    
    # Test 1: Check status
    print("\n1. Checking ML service status...")
    try:
        response = requests.get(f"{base_url}/api/v1/ml/status", timeout=5)
        print(f"   Status code: {response.status_code}")
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Model loaded: {data.get('model_loaded')}")
        if data.get('error'):
            print(f"   Error: {data['error']}")
    except requests.exceptions.ConnectionError:
        print("   ✗ Cannot connect to server. Is it running?")
        print(f"   Try: cd app && uv run uvicorn app.main:app --reload")
        return
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Get recommendations without phone (new user)
    print("\n2. Getting recommendations (new user, no phone)...")
    try:
        payload = {
            "phone": None,
            "current_cart": ["Роллы", "Кола"],
            "limit": 3
        }
        response = requests.post(
            f"{base_url}/api/v1/ml/recommendations/ml",
            json=payload,
            timeout=10
        )
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Source: {data.get('source')}")
            print(f"   Time: {data.get('processing_time_ms'):.2f}ms")
            print(f"   Recommendations ({len(data.get('recommendations', []))} found):")
            for rec in data.get("recommendations", [])[:3]:
                print(f"     - {rec['name']} ({rec['category']}) - {rec['price_rub']}₽ [confidence: {rec['confidence']:.2f}]")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Get recommendations with phone (returning customer)
    print("\n3. Getting recommendations (with phone)...")
    try:
        payload = {
            "phone": "+79991234567",
            "current_cart": ["Пицца Маргарита"],
            "limit": 5
        }
        response = requests.post(
            f"{base_url}/api/v1/ml/recommendations/ml",
            json=payload,
            timeout=10
        )
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Source: {data.get('source')}")
            print(f"   User orders: {data.get('user_order_count', 'N/A')}")
            print(f"   Time: {data.get('processing_time_ms'):.2f}ms")
            print(f"   Recommendations ({len(data.get('recommendations', []))} found):")
            for rec in data.get("recommendations", [])[:3]:
                print(f"     - {rec['name']} ({rec['category']}) - {rec['price_rub']}₽ [confidence: {rec['confidence']:.2f}]")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Test with limit
    print("\n4. Testing limit parameter...")
    try:
        payload = {
            "phone": None,
            "current_cart": ["Роллы"],
            "limit": 10
        }
        response = requests.post(
            f"{base_url}/api/v1/ml/recommendations/ml",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get("recommendations", []))
            print(f"   Requested limit: 10")
            print(f"   Got: {count} recommendations")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test ML recommendation API")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    test_api(args.url)
