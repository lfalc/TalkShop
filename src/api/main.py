from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import logging
from contextlib import asynccontextmanager

from .database import db
from .models import (
    UserProfile, Product, UserProductInteraction, InteractionWithProduct,
    ProductSearchParams, SentimentByAttributesParams, SentimentEnum
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    logger.info("TalkShop API started")
    yield
    # Shutdown
    await db.disconnect()
    logger.info("TalkShop API stopped")


app = FastAPI(
    title="TalkShop API",
    description="API for product memory and user sentiment tracking",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "TalkShop API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# User endpoints
@app.get("/read/user/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    """Get user profile by user_id"""
    user_data = await db.get_user_profile(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(**user_data)


@app.get("/read/user/{user_id}/interactions", response_model=List[InteractionWithProduct])
async def get_user_interactions(
    user_id: str,
    sentiment: Optional[SentimentEnum] = Query(None, description="Filter by sentiment"),
    limit: int = Query(50, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get user interactions with full product details"""
    interactions = await db.get_user_interactions(
        user_id=user_id, 
        sentiment=sentiment.value if sentiment else None,
        limit=limit,
        offset=offset
    )
    return [InteractionWithProduct(**interaction) for interaction in interactions]


@app.get("/read/user/{user_id}/sentiment-by-attributes", response_model=List[InteractionWithProduct])
async def get_user_sentiment_by_attributes(
    user_id: str,
    brand: Optional[List[str]] = Query(None, description="Filter by brands"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sub_category: Optional[str] = Query(None, description="Filter by sub_category"),
    style_tags: Optional[List[str]] = Query(None, description="Filter by style tags"),
    colors: Optional[List[str]] = Query(None, description="Filter by colors"),
    materials: Optional[List[str]] = Query(None, description="Filter by materials"),
    use_cases: Optional[List[str]] = Query(None, description="Filter by use cases"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    sentiment: Optional[SentimentEnum] = Query(None, description="Filter by sentiment"),
    limit: int = Query(50, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get user sentiment for products matching specific attributes with full product details"""
    params = {
        "brand": brand,
        "category": category,
        "sub_category": sub_category,
        "style_tags": style_tags,
        "colors": colors,
        "materials": materials,
        "use_cases": use_cases,
        "price_min": price_min,
        "price_max": price_max,
        "sentiment": sentiment.value if sentiment else None,
        "limit": limit,
        "offset": offset
    }
    
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    interactions = await db.get_sentiment_by_attributes(user_id, params)
    return [InteractionWithProduct(**interaction) for interaction in interactions]


# Product endpoints
@app.get("/read/product/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get product by product_id"""
    product_data = await db.get_product(product_id)
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product_data)


@app.get("/read/product/{product_id}/interactions", response_model=List[InteractionWithProduct])
async def get_product_interactions(
    product_id: str,
    sentiment: Optional[SentimentEnum] = Query(None, description="Filter by sentiment"),
    limit: int = Query(50, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get product interactions with full product details"""
    interactions = await db.get_product_interactions(
        product_id=product_id,
        sentiment=sentiment.value if sentiment else None,
        limit=limit,
        offset=offset
    )
    return [InteractionWithProduct(**interaction) for interaction in interactions]


@app.get("/read/products/search", response_model=List[Product])
async def search_products(
    brand: Optional[List[str]] = Query(None, description="Filter by brands"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sub_category: Optional[str] = Query(None, description="Filter by sub_category"),
    style_tags: Optional[List[str]] = Query(None, description="Filter by style tags"),
    colors: Optional[List[str]] = Query(None, description="Filter by colors"),
    materials: Optional[List[str]] = Query(None, description="Filter by materials"),
    use_cases: Optional[List[str]] = Query(None, description="Filter by use cases"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    size: Optional[str] = Query(None, description="Filter by size"),
    text: Optional[str] = Query(None, description="Text search in name and brand"),
    limit: int = Query(20, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Search products by attributes and other criteria"""
    params = {
        "brand": brand,
        "category": category,
        "sub_category": sub_category,
        "style_tags": style_tags,
        "colors": colors,
        "materials": materials,
        "use_cases": use_cases,
        "price_min": price_min,
        "price_max": price_max,
        "size": size,
        "text": text,
        "limit": limit,
        "offset": offset
    }
    
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    products = await db.search_products(params)
    return [Product(**product) for product in products]


# General interaction endpoints
@app.get("/read/interactions", response_model=List[InteractionWithProduct])
async def get_interactions(
    user_id: Optional[str] = Query(None, description="Filter by user_id"),
    product_id: Optional[str] = Query(None, description="Filter by product_id"),
    sentiment: Optional[SentimentEnum] = Query(None, description="Filter by sentiment"),
    limit: int = Query(50, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get interactions with optional filters and full product details"""
    if user_id and product_id:
        # Get specific user-product interaction
        interactions = await db.get_user_interactions(
            user_id=user_id,
            sentiment=sentiment.value if sentiment else None,
            limit=limit,
            offset=offset
        )
        # Filter by product_id
        interactions = [i for i in interactions if i["product_id"] == product_id]
    elif user_id:
        # Get user interactions
        interactions = await db.get_user_interactions(
            user_id=user_id,
            sentiment=sentiment.value if sentiment else None,
            limit=limit,
            offset=offset
        )
    elif product_id:
        # Get product interactions
        interactions = await db.get_product_interactions(
            product_id=product_id,
            sentiment=sentiment.value if sentiment else None,
            limit=limit,
            offset=offset
        )
    else:
        # This would require a separate method for all interactions
        # For now, return empty list or implement if needed
        interactions = []
    
    return [InteractionWithProduct(**interaction) for interaction in interactions]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)