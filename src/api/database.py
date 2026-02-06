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


    # Write/Create methods
    async def create_user_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user profile"""
        query = """
        INSERT INTO user_profiles (
            user_id, gender, products, metadata, profile_created_at,
            profile_last_updated, total_selections, total_rejections, profile_confidence
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                query,
                user_data.get('user_id'),
                user_data.get('gender'),
                json.dumps(user_data.get('products', {})),
                json.dumps(user_data.get('metadata', {})),
                user_data.get('profile_created_at'),
                user_data.get('profile_last_updated'),
                user_data.get('total_selections', 0),
                user_data.get('total_rejections', 0),
                user_data.get('profile_confidence')
            )
            
            if row:
                result = dict(row)
                return _parse_jsonb_fields(result, ['products', 'metadata'])
            return None

    async def update_user_profile(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing user profile"""
        # Build dynamic UPDATE query based on provided fields
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in user_data.items():
            if value is not None:
                param_count += 1
                if field in ['products', 'metadata']:
                    update_fields.append(f"{field} = ${param_count}::jsonb")
                    params.append(json.dumps(value))
                else:
                    update_fields.append(f"{field} = ${param_count}")
                    params.append(value)
        
        if not update_fields:
            # No fields to update, return existing user
            return await self.get_user_profile(user_id)
        
        # Add updated_at automatically  
        update_fields.append(f"updated_at = NOW()")
        
        # Add user_id for WHERE clause
        param_count += 1
        params.append(user_id)
        
        query = f"""
        UPDATE user_profiles 
        SET {', '.join(update_fields)}
        WHERE user_id = ${param_count}
        RETURNING *
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *params)
            if row:
                result = dict(row)
                return _parse_jsonb_fields(result, ['products', 'metadata'])
            return None

    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product"""
        query = """
        INSERT INTO products (
            product_id, name, brand, category, sub_category, price, currency,
            size, color, material, attributes, product_url, image_path,
            product_summary, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        RETURNING *
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                query,
                product_data.get('product_id'),
                product_data.get('name'),
                product_data.get('brand'),
                product_data.get('category'),
                product_data.get('sub_category'),
                product_data.get('price'),
                product_data.get('currency', 'USD'),
                product_data.get('size'),
                product_data.get('color'),
                product_data.get('material'),
                json.dumps(product_data.get('attributes', {})),
                product_data.get('product_url'),
                product_data.get('image_path'),
                product_data.get('product_summary'),
                json.dumps(product_data.get('metadata', {}))
            )
            
            if row:
                result = dict(row)
                return _parse_jsonb_fields(result, ['attributes', 'metadata'])
            return None

    async def update_product(self, product_id: str, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing product"""
        # Build dynamic UPDATE query based on provided fields
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in product_data.items():
            if value is not None:
                param_count += 1
                if field in ['attributes', 'metadata']:
                    update_fields.append(f"{field} = ${param_count}::jsonb")
                    params.append(json.dumps(value))
                else:
                    update_fields.append(f"{field} = ${param_count}")
                    params.append(value)
        
        if not update_fields:
            # No fields to update, return existing product
            return await self.get_product(product_id)
        
        # Add updated_at automatically  
        update_fields.append(f"updated_at = NOW()")
        
        # Add product_id for WHERE clause
        param_count += 1
        params.append(product_id)
        
        query = f"""
        UPDATE products 
        SET {', '.join(update_fields)}
        WHERE product_id = ${param_count}
        RETURNING *
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *params)
            if row:
                result = dict(row)
                return _parse_jsonb_fields(result, ['attributes', 'metadata'])
            return None

    async def create_user_product_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user-product interaction"""
        query = """
        INSERT INTO user_product_interactions (user_id, product_id, sentiment, sentiment_notes)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                query,
                interaction_data.get('user_id'),
                interaction_data.get('product_id'),
                interaction_data.get('sentiment'),
                interaction_data.get('sentiment_notes')
            )
            return dict(row) if row else None

    async def update_user_product_interaction(
        self, 
        user_id: str, 
        product_id: str, 
        interaction_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing user-product interaction"""
        # Build dynamic UPDATE query based on provided fields
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in interaction_data.items():
            if value is not None:
                param_count += 1
                update_fields.append(f"{field} = ${param_count}")
                params.append(value)
        
        if not update_fields:
            # No fields to update, try to get existing interaction
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM user_product_interactions WHERE user_id = $1 AND product_id = $2",
                    user_id, product_id
                )
                return dict(row) if row else None
        
        # Add updated_at automatically  
        update_fields.append(f"updated_at = NOW()")
        
        # Add user_id and product_id for WHERE clause
        param_count += 1
        params.append(user_id)
        param_count += 1
        params.append(product_id)
        
        query = f"""
        UPDATE user_product_interactions 
        SET {', '.join(update_fields)}
        WHERE user_id = ${param_count-1} AND product_id = ${param_count}
        RETURNING *
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *params)
            return dict(row) if row else None

    async def delete_user_profile(self, user_id: str) -> bool:
        """Delete a user profile"""
        async with self.get_connection() as conn:
            result = await conn.execute(
                "DELETE FROM user_profiles WHERE user_id = $1",
                user_id
            )
            return result == "DELETE 1"

    async def delete_product(self, product_id: str) -> bool:
        """Delete a product"""
        async with self.get_connection() as conn:
            result = await conn.execute(
                "DELETE FROM products WHERE product_id = $1",
                product_id
            )
            return result == "DELETE 1"

    async def delete_user_product_interaction(self, user_id: str, product_id: str) -> bool:
        """Delete a user-product interaction"""
        async with self.get_connection() as conn:
            result = await conn.execute(
                "DELETE FROM user_product_interactions WHERE user_id = $1 AND product_id = $2",
                user_id, product_id
            )
            return result == "DELETE 1"


# Global database instance
db = Database()