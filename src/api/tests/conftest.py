import pytest
import pytest_asyncio
import os
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from typing import Dict, Any, List

# Set test environment
os.environ["DATABASE_URL"] = "postgresql://test_user:test_pass@localhost:5432/test_db"

from api.main import app
from api.database import db


@pytest_asyncio.fixture
async def mock_db():
    """Mock database for testing"""
    original_db = db
    
    # Create mock database instance
    mock_db_instance = AsyncMock()
    
    # Replace the global db instance
    import api.main
    import api.database
    api.main.db = mock_db_instance
    api.database.db = mock_db_instance
    
    yield mock_db_instance
    
    # Restore original
    api.main.db = original_db
    api.database.db = original_db


@pytest_asyncio.fixture
async def test_client(mock_db):
    """Test client for FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_user_profile():
    """Sample user profile data"""
    return {
        "user_id": "usr_test_001",
        "gender": "female",
        "products": {
            "shoe": {
                "size": "8.5",
                "attributes": {
                    "brands": {"preferred": ["Gucci", "Balenciaga"], "avoided": ["budget-brands"]},
                    "types": {"preferred": ["sneaker", "boot"], "avoided": ["athletic"]},
                    "colors": {"preferred": ["white", "black"], "avoided": ["neon"]},
                    "materials": {"preferred": ["leather"], "avoided": ["synthetic"]},
                    "price_range": {"min": 300, "max": 1200, "currency": "USD"},
                    "style_tags": ["luxury", "designer", "minimalist"]
                }
            }
        },
        "metadata": {},
        "profile_created_at": datetime(2026, 1, 8, 9, 45, 0),
        "profile_last_updated": datetime(2026, 2, 6, 10, 5, 0),
        "total_selections": 39,
        "total_rejections": 24,
        "profile_confidence": 0.88,
        "created_at": datetime(2026, 1, 8, 9, 45, 0),
        "updated_at": datetime(2026, 2, 6, 10, 5, 0)
    }


@pytest.fixture
def sample_products():
    """Sample product data"""
    return [
        {
            "product_id": "prd_gucci_sneaker_001",
            "name": "Ace Leather Sneaker",
            "brand": "Gucci",
            "category": "shoe",
            "sub_category": "sneaker",
            "price": 690.00,
            "currency": "USD",
            "size": "8.5",
            "color": "white",
            "material": "leather",
            "attributes": {
                "brands": ["Gucci"],
                "types": ["sneaker"],
                "colors": ["white"],
                "materials": ["leather"],
                "style_tags": ["luxury", "designer", "minimalist"],
                "use_cases": ["casual-chic", "events"]
            },
            "product_url": "https://www.gucci.com/sneaker",
            "image_path": "products/shoes/prd_gucci_sneaker_001.jpg",
            "product_summary": "Classic Gucci Ace sneaker with white leather construction",
            "metadata": {},
            "created_at": datetime(2026, 2, 1, 10, 0, 0),
            "updated_at": datetime(2026, 2, 1, 10, 0, 0)
        },
        {
            "product_id": "prd_nike_athletic_001",
            "name": "Air Max 270",
            "brand": "Nike",
            "category": "shoe",
            "sub_category": "athletic",
            "price": 150.00,
            "currency": "USD",
            "size": "10",
            "color": "black",
            "material": "knit",
            "attributes": {
                "brands": ["Nike"],
                "types": ["athletic", "sneaker"],
                "colors": ["black", "white"],
                "materials": ["knit"],
                "style_tags": ["sporty", "modern"],
                "use_cases": ["gym", "casual", "running"]
            },
            "product_url": "https://www.nike.com/air-max-270",
            "image_path": "products/shoes/prd_nike_athletic_001.jpg",
            "product_summary": "Nike Air Max 270 with large heel Air unit",
            "metadata": {},
            "created_at": datetime(2026, 2, 1, 11, 0, 0),
            "updated_at": datetime(2026, 2, 1, 11, 0, 0)
        }
    ]


@pytest.fixture
def sample_interactions():
    """Sample interaction data with product details"""
    return [
        {
            "interaction_id": "int_001",
            "user_id": "usr_test_001",
            "product_id": "prd_gucci_sneaker_001",
            "sentiment": "good",
            "sentiment_notes": "Love the clean white leather and luxury branding",
            "interaction_created_at": datetime(2026, 2, 5, 14, 30, 0),
            "interaction_updated_at": datetime(2026, 2, 5, 14, 30, 0),
            # Product details from JOIN
            "product_name": "Ace Leather Sneaker",
            "brand": "Gucci",
            "category": "shoe",
            "sub_category": "sneaker",
            "price": 690.00,
            "currency": "USD",
            "size": "8.5",
            "color": "white",
            "material": "leather",
            "attributes": {
                "brands": ["Gucci"],
                "types": ["sneaker"],
                "colors": ["white"],
                "materials": ["leather"],
                "style_tags": ["luxury", "designer", "minimalist"],
                "use_cases": ["casual-chic", "events"]
            },
            "product_url": "https://www.gucci.com/sneaker",
            "image_path": "products/shoes/prd_gucci_sneaker_001.jpg",
            "product_summary": "Classic Gucci Ace sneaker with white leather construction",
            "product_metadata": {},
            "product_created_at": datetime(2026, 2, 1, 10, 0, 0),
            "product_updated_at": datetime(2026, 2, 1, 10, 0, 0)
        },
        {
            "interaction_id": "int_002",
            "user_id": "usr_test_001",
            "product_id": "prd_nike_athletic_001",
            "sentiment": "bad",
            "sentiment_notes": "Too athletic-focused for my style preferences",
            "interaction_created_at": datetime(2026, 2, 4, 12, 15, 0),
            "interaction_updated_at": datetime(2026, 2, 4, 12, 15, 0),
            # Product details from JOIN
            "product_name": "Air Max 270",
            "brand": "Nike",
            "category": "shoe",
            "sub_category": "athletic",
            "price": 150.00,
            "currency": "USD",
            "size": "10",
            "color": "black",
            "material": "knit",
            "attributes": {
                "brands": ["Nike"],
                "types": ["athletic", "sneaker"],
                "colors": ["black", "white"],
                "materials": ["knit"],
                "style_tags": ["sporty", "modern"],
                "use_cases": ["gym", "casual", "running"]
            },
            "product_url": "https://www.nike.com/air-max-270",
            "image_path": "products/shoes/prd_nike_athletic_001.jpg",
            "product_summary": "Nike Air Max 270 with large heel Air unit",
            "product_metadata": {},
            "product_created_at": datetime(2026, 2, 1, 11, 0, 0),
            "product_updated_at": datetime(2026, 2, 1, 11, 0, 0)
        }
    ]