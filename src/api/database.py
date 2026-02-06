import asyncpg
import json
import os
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


def _parse_jsonb_fields(row_dict: Dict[str, Any], jsonb_fields: List[str]) -> Dict[str, Any]:
    """Helper function to parse JSONB fields from string to dict"""
    for field in jsonb_fields:
        if row_dict.get(field) and isinstance(row_dict[field], str):
            try:
                row_dict[field] = json.loads(row_dict[field])
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to parse JSONB field {field}: {row_dict[field]}")
                row_dict[field] = {}
    return row_dict


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize database connection pool"""
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.pool = await asyncpg.create_pool(
            database_url,
            min_size=1,
            max_size=10,
            command_timeout=60,
            statement_cache_size=0  # Required for Supabase pgbouncer
        )
        logger.info("Database connection pool created")

    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool"""
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as connection:
            yield connection

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by user_id"""
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM user_profiles WHERE user_id = $1",
                user_id
            )
            if not row:
                return None
            
            result = dict(row)
            return _parse_jsonb_fields(result, ['products', 'metadata'])

    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by product_id"""
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM products WHERE product_id = $1",
                product_id
            )
            if not row:
                return None
            
            result = dict(row)
            return _parse_jsonb_fields(result, ['attributes', 'metadata'])

    async def get_user_interactions(
        self, 
        user_id: str, 
        sentiment: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user interactions with full product details via JOIN"""
        query = """
        SELECT 
            upi.interaction_id,
            upi.user_id,
            upi.product_id,
            upi.sentiment,
            upi.sentiment_notes,
            upi.created_at as interaction_created_at,
            upi.updated_at as interaction_updated_at,
            p.name as product_name,
            p.brand,
            p.category,
            p.sub_category,
            p.price,
            p.currency,
            p.size,
            p.color,
            p.material,
            p.attributes,
            p.product_url,
            p.image_path,
            p.product_summary,
            p.metadata as product_metadata,
            p.created_at as product_created_at,
            p.updated_at as product_updated_at
        FROM user_product_interactions upi
        JOIN products p ON upi.product_id = p.product_id
        WHERE upi.user_id = $1
        """
        params = [user_id]
        
        if sentiment:
            query += " AND upi.sentiment = $2"
            params.append(sentiment)
            query += " ORDER BY upi.created_at DESC LIMIT $3 OFFSET $4"
            params.extend([limit, offset])
        else:
            query += " ORDER BY upi.created_at DESC LIMIT $2 OFFSET $3"
            params.extend([limit, offset])
        
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *params)
            results = [dict(row) for row in rows]
            # Parse JSONB fields for each interaction with product details
            return [_parse_jsonb_fields(result, ['attributes', 'product_metadata']) for result in results]

    async def get_product_interactions(
        self,
        product_id: str,
        sentiment: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get product interactions with full product details via JOIN"""
        query = """
        SELECT 
            upi.interaction_id,
            upi.user_id,
            upi.product_id,
            upi.sentiment,
            upi.sentiment_notes,
            upi.created_at as interaction_created_at,
            upi.updated_at as interaction_updated_at,
            p.name as product_name,
            p.brand,
            p.category,
            p.sub_category,
            p.price,
            p.currency,
            p.size,
            p.color,
            p.material,
            p.attributes,
            p.product_url,
            p.image_path,
            p.product_summary,
            p.metadata as product_metadata,
            p.created_at as product_created_at,
            p.updated_at as product_updated_at
        FROM user_product_interactions upi
        JOIN products p ON upi.product_id = p.product_id
        WHERE upi.product_id = $1
        """
        params = [product_id]
        
        if sentiment:
            query += " AND upi.sentiment = $2"
            params.append(sentiment)
            query += " ORDER BY upi.created_at DESC LIMIT $3 OFFSET $4"
            params.extend([limit, offset])
        else:
            query += " ORDER BY upi.created_at DESC LIMIT $2 OFFSET $3"
            params.extend([limit, offset])
        
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *params)
            results = [dict(row) for row in rows]
            # Parse JSONB fields for each interaction with product details
            return [_parse_jsonb_fields(result, ['attributes', 'product_metadata']) for result in results]

    async def search_products(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search products by attributes and filters"""
        conditions = []
        query_params = []
        param_count = 0

        base_query = "SELECT * FROM products WHERE 1=1"
        
        # Brand filter
        if params.get("brand"):
            param_count += 1
            conditions.append(f"brand = ANY(${param_count})")
            query_params.append(params["brand"])
        
        # Category filters
        if params.get("category"):
            param_count += 1
            conditions.append(f"category = ${param_count}")
            query_params.append(params["category"])
            
        if params.get("sub_category"):
            param_count += 1
            conditions.append(f"sub_category = ${param_count}")
            query_params.append(params["sub_category"])
        
        # Price filters
        if params.get("price_min") is not None:
            param_count += 1
            conditions.append(f"price >= ${param_count}")
            query_params.append(params["price_min"])
            
        if params.get("price_max") is not None:
            param_count += 1
            conditions.append(f"price <= ${param_count}")
            query_params.append(params["price_max"])
        
        # Size filter
        if params.get("size"):
            param_count += 1
            conditions.append(f"size = ${param_count}")
            query_params.append(params["size"])
        
        # JSONB attribute filters
        jsonb_filters = ["style_tags", "colors", "materials", "use_cases"]
        for filter_name in jsonb_filters:
            if params.get(filter_name):
                param_count += 1
                conditions.append(f"attributes @> ${param_count}::jsonb")
                query_params.append(json.dumps({filter_name: params[filter_name]}))
        
        # Text search
        if params.get("text"):
            param_count += 1
            conditions.append(f"to_tsvector('english', name || ' ' || COALESCE(brand, '')) @@ plainto_tsquery(${param_count})")
            query_params.append(params["text"])
        
        # Build final query
        if conditions:
            query = base_query + " AND " + " AND ".join(conditions)
        else:
            query = base_query
        
        # Add ordering and pagination
        query += " ORDER BY created_at DESC"
        
        limit = params.get("limit", 20)
        offset = params.get("offset", 0)
        param_count += 1
        query += f" LIMIT ${param_count}"
        query_params.append(limit)
        
        param_count += 1
        query += f" OFFSET ${param_count}"
        query_params.append(offset)
        
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *query_params)
            results = [dict(row) for row in rows]
            # Parse JSONB fields for each product
            return [_parse_jsonb_fields(result, ['attributes', 'metadata']) for result in results]

    async def get_sentiment_by_attributes(
        self, 
        user_id: str, 
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get user sentiment for products matching specific attributes with full product details"""
        conditions = ["upi.user_id = $1"]
        query_params = [user_id]
        param_count = 1

        base_query = """
        SELECT 
            upi.interaction_id,
            upi.user_id,
            upi.product_id,
            upi.sentiment,
            upi.sentiment_notes,
            upi.created_at as interaction_created_at,
            upi.updated_at as interaction_updated_at,
            p.name as product_name,
            p.brand,
            p.category,
            p.sub_category,
            p.price,
            p.currency,
            p.size,
            p.color,
            p.material,
            p.attributes,
            p.product_url,
            p.image_path,
            p.product_summary,
            p.metadata as product_metadata,
            p.created_at as product_created_at,
            p.updated_at as product_updated_at
        FROM user_product_interactions upi
        JOIN products p ON upi.product_id = p.product_id
        WHERE upi.user_id = $1
        """
        
        # Brand filter
        if params.get("brand"):
            param_count += 1
            conditions.append(f"p.brand = ANY(${param_count})")
            query_params.append(params["brand"])
        
        # Category filters
        if params.get("category"):
            param_count += 1
            conditions.append(f"p.category = ${param_count}")
            query_params.append(params["category"])
            
        if params.get("sub_category"):
            param_count += 1
            conditions.append(f"p.sub_category = ${param_count}")
            query_params.append(params["sub_category"])
        
        # Price filters
        if params.get("price_min") is not None:
            param_count += 1
            conditions.append(f"p.price >= ${param_count}")
            query_params.append(params["price_min"])
            
        if params.get("price_max") is not None:
            param_count += 1
            conditions.append(f"p.price <= ${param_count}")
            query_params.append(params["price_max"])
        
        # JSONB attribute filters
        jsonb_filters = ["style_tags", "colors", "materials", "use_cases"]
        for filter_name in jsonb_filters:
            if params.get(filter_name):
                param_count += 1
                conditions.append(f"p.attributes @> ${param_count}::jsonb")
                query_params.append(json.dumps({filter_name: params[filter_name]}))
        
        # Sentiment filter
        if params.get("sentiment"):
            param_count += 1
            conditions.append(f"upi.sentiment = ${param_count}")
            query_params.append(params["sentiment"])
        
        # Build final query
        query = base_query + " AND " + " AND ".join(conditions[1:]) if len(conditions) > 1 else base_query
        
        # Add ordering and pagination
        query += " ORDER BY upi.created_at DESC"
        
        limit = params.get("limit", 50)
        offset = params.get("offset", 0)
        param_count += 1
        query += f" LIMIT ${param_count}"
        query_params.append(limit)
        
        param_count += 1
        query += f" OFFSET ${param_count}"
        query_params.append(offset)
        
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *query_params)
            results = [dict(row) for row in rows]
            # Parse JSONB fields for each interaction with product details
            return [_parse_jsonb_fields(result, ['attributes', 'product_metadata']) for result in results]


# Global database instance
db = Database()