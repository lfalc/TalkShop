import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock


class TestProductSearch:
    """Test product search endpoint functionality"""

    async def test_search_products_by_brand(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by brand"""
        # Mock database response - only Gucci products
        gucci_products = [p for p in sample_products if p["brand"] == "Gucci"]
        mock_db.search_products.return_value = gucci_products
        
        # Make request
        response = await test_client.get("/read/products/search?brand=Gucci")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["brand"] == "Gucci"
        assert data[0]["name"] == "Ace Leather Sneaker"
        
        # Verify database call
        mock_db.search_products.assert_called_once()
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["brand"] == ["Gucci"]

    async def test_search_products_by_multiple_brands(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by multiple brands"""
        mock_db.search_products.return_value = sample_products
        
        # Make request with multiple brands
        response = await test_client.get("/read/products/search?brand=Gucci&brand=Nike")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["brand"] == ["Gucci", "Nike"]

    async def test_search_products_by_category(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by category"""
        # Mock database response - all shoes
        shoe_products = [p for p in sample_products if p["category"] == "shoe"]
        mock_db.search_products.return_value = shoe_products
        
        # Make request
        response = await test_client.get("/read/products/search?category=shoe")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(p["category"] == "shoe" for p in data)
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["category"] == "shoe"

    async def test_search_products_by_category_and_sub_category(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by category and sub_category"""
        # Mock database response - sneakers only
        sneaker_products = [
            p for p in sample_products 
            if p["category"] == "shoe" and p["sub_category"] == "sneaker"
        ]
        mock_db.search_products.return_value = sneaker_products
        
        # Make request
        response = await test_client.get("/read/products/search?category=shoe&sub_category=sneaker")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sub_category"] == "sneaker"
        assert data[0]["brand"] == "Gucci"
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["category"] == "shoe"
        assert call_args[0][0]["sub_category"] == "sneaker"

    async def test_search_products_by_price_range(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by price range"""
        # Mock database response - products in price range
        price_filtered = [p for p in sample_products if 100 <= p["price"] <= 200]
        mock_db.search_products.return_value = price_filtered
        
        # Make request
        response = await test_client.get("/read/products/search?price_min=100&price_max=200")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["price"] == 150.00
        assert data[0]["brand"] == "Nike"
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["price_min"] == 100
        assert call_args[0][0]["price_max"] == 200

    async def test_search_products_by_style_tags(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by style tags"""
        # Mock database response - luxury items
        luxury_products = [
            p for p in sample_products 
            if "luxury" in p["attributes"].get("style_tags", [])
        ]
        mock_db.search_products.return_value = luxury_products
        
        # Make request
        response = await test_client.get("/read/products/search?style_tags=luxury")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "luxury" in data[0]["attributes"]["style_tags"]
        assert data[0]["brand"] == "Gucci"
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["style_tags"] == ["luxury"]

    async def test_search_products_by_multiple_style_tags(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by multiple style tags"""
        mock_db.search_products.return_value = sample_products
        
        # Make request
        response = await test_client.get("/read/products/search?style_tags=luxury&style_tags=sporty")
        
        # Verify response
        assert response.status_code == 200
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["style_tags"] == ["luxury", "sporty"]

    async def test_search_products_by_colors(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by colors"""
        # Mock database response - white products
        white_products = [
            p for p in sample_products 
            if "white" in p["attributes"].get("colors", [])
        ]
        mock_db.search_products.return_value = white_products
        
        # Make request
        response = await test_client.get("/read/products/search?colors=white")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "white" in data[0]["attributes"]["colors"]
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["colors"] == ["white"]

    async def test_search_products_by_materials(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by materials"""
        # Mock database response - leather products
        leather_products = [
            p for p in sample_products 
            if "leather" in p["attributes"].get("materials", [])
        ]
        mock_db.search_products.return_value = leather_products
        
        # Make request
        response = await test_client.get("/read/products/search?materials=leather")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "leather" in data[0]["attributes"]["materials"]
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["materials"] == ["leather"]

    async def test_search_products_by_use_cases(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by use cases"""
        # Mock database response - casual products
        casual_products = [
            p for p in sample_products 
            if "casual" in p["attributes"].get("use_cases", [])
        ]
        mock_db.search_products.return_value = casual_products
        
        # Make request
        response = await test_client.get("/read/products/search?use_cases=casual")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "casual" in data[0]["attributes"]["use_cases"]
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["use_cases"] == ["casual"]

    async def test_search_products_by_size(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by size"""
        # Mock database response - specific size
        size_filtered = [p for p in sample_products if p["size"] == "8.5"]
        mock_db.search_products.return_value = size_filtered
        
        # Make request
        response = await test_client.get("/read/products/search?size=8.5")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["size"] == "8.5"
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["size"] == "8.5"

    async def test_search_products_by_text(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products by text"""
        # Mock database response - text search results
        nike_products = [p for p in sample_products if "Nike" in p["name"] or p["brand"] == "Nike"]
        mock_db.search_products.return_value = nike_products
        
        # Make request
        response = await test_client.get("/read/products/search?text=Nike")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["brand"] == "Nike"
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        assert call_args[0][0]["text"] == "Nike"

    async def test_search_products_complex_filter(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products with complex filter combination"""
        # Mock database response - empty for complex filter
        mock_db.search_products.return_value = []
        
        # Make request with multiple filters
        response = await test_client.get(
            "/read/products/search"
            "?brand=Gucci&category=shoe&style_tags=luxury&materials=leather&price_min=500&price_max=1000"
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        
        # Verify database call includes all filters
        call_args = mock_db.search_products.call_args
        params = call_args[0][0]
        assert params["brand"] == ["Gucci"]
        assert params["category"] == "shoe"
        assert params["style_tags"] == ["luxury"]
        assert params["materials"] == ["leather"]
        assert params["price_min"] == 500
        assert params["price_max"] == 1000

    async def test_search_products_with_pagination(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products with pagination"""
        mock_db.search_products.return_value = sample_products[1:]  # Skip first
        
        # Make request with pagination
        response = await test_client.get("/read/products/search?category=shoe&limit=10&offset=1")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Verify database call includes pagination
        call_args = mock_db.search_products.call_args
        params = call_args[0][0]
        assert params["limit"] == 10
        assert params["offset"] == 1
        assert params["category"] == "shoe"

    async def test_search_products_default_pagination(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products with default pagination values"""
        mock_db.search_products.return_value = sample_products
        
        # Make request without explicit pagination
        response = await test_client.get("/read/products/search?brand=Nike")
        
        # Verify response
        assert response.status_code == 200
        
        # Verify database call uses default pagination
        call_args = mock_db.search_products.call_args
        params = call_args[0][0]
        assert params["limit"] == 20  # Default limit
        assert params["offset"] == 0   # Default offset

    async def test_search_products_no_filters(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products with no filters (should return all products)"""
        mock_db.search_products.return_value = sample_products
        
        # Make request with no filters
        response = await test_client.get("/read/products/search")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify database call
        call_args = mock_db.search_products.call_args
        params = call_args[0][0]
        # Should only have default pagination params
        assert params.get("limit") == 20
        assert params.get("offset") == 0

    async def test_search_products_empty_results(self, test_client: AsyncClient, mock_db: AsyncMock):
        """Test searching products with no results"""
        mock_db.search_products.return_value = []
        
        # Make request for non-existent brand
        response = await test_client.get("/read/products/search?brand=NonexistentBrand")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        assert data == []

    async def test_search_products_pagination_limits(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test searching products with pagination limits"""
        mock_db.search_products.return_value = sample_products
        
        # Test maximum limit
        response = await test_client.get("/read/products/search?limit=100")
        assert response.status_code == 200
        
        # Test exceeding maximum limit (should be capped)
        response = await test_client.get("/read/products/search?limit=150")
        assert response.status_code == 422  # Validation error
        
        # Test negative offset (should be rejected)
        response = await test_client.get("/read/products/search?offset=-1")
        assert response.status_code == 422  # Validation error

    async def test_search_products_returns_all_fields(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test that product search returns all expected fields"""
        mock_db.search_products.return_value = sample_products[:1]
        
        # Make request
        response = await test_client.get("/read/products/search?brand=Gucci")
        
        # Verify response includes all product fields
        assert response.status_code == 200
        data = response.json()
        product = data[0]
        
        # Check all expected fields are present
        expected_fields = [
            "product_id", "name", "brand", "category", "sub_category",
            "price", "currency", "size", "color", "material", "attributes",
            "product_url", "image_path", "product_summary", "metadata",
            "created_at", "updated_at"
        ]
        
        for field in expected_fields:
            assert field in product, f"Field '{field}' missing from product response"