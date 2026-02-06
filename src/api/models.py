from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SentimentEnum(str, Enum):
    good = "good"
    bad = "bad"


class UserProfile(BaseModel):
    user_id: str
    gender: Optional[str] = None
    products: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    profile_created_at: Optional[datetime] = None
    profile_last_updated: Optional[datetime] = None
    total_selections: Optional[int] = None
    total_rejections: Optional[int] = None
    profile_confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class Product(BaseModel):
    product_id: str
    name: str
    brand: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "USD"
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    attributes: Dict[str, Any] = {}
    product_url: Optional[str] = None
    image_path: Optional[str] = None
    product_summary: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class UserProductInteraction(BaseModel):
    interaction_id: str
    user_id: str
    product_id: str
    sentiment: SentimentEnum
    sentiment_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class InteractionWithProduct(BaseModel):
    """User interaction joined with full product details"""
    interaction_id: str
    user_id: str
    product_id: str
    sentiment: SentimentEnum
    sentiment_notes: Optional[str] = None
    interaction_created_at: datetime
    interaction_updated_at: datetime
    
    # Product details
    product_name: str
    brand: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "USD"
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    attributes: Dict[str, Any] = {}
    product_url: Optional[str] = None
    image_path: Optional[str] = None
    product_summary: Optional[str] = None
    product_metadata: Dict[str, Any] = {}
    product_created_at: datetime
    product_updated_at: datetime


class ProductSearchParams(BaseModel):
    brand: Optional[List[str]] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    style_tags: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    size: Optional[str] = None
    text: Optional[str] = None
    limit: Optional[int] = Field(default=20, le=100)
    offset: Optional[int] = Field(default=0, ge=0)


class SentimentByAttributesParams(BaseModel):
    brand: Optional[List[str]] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    style_tags: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    sentiment: Optional[SentimentEnum] = None
    limit: Optional[int] = Field(default=50, le=100)
    offset: Optional[int] = Field(default=0, ge=0)