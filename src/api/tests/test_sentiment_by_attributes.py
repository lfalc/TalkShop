import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock


class TestSentimentByAttributes:
    """Test sentiment-by-attributes endpoint functionality"""

    async def test_sentiment_by_brand(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test filtering sentiment by brand"""
        # Mock database response - only Gucci interactions
        gucci_interactions = [i for i in sample_interactions if i["brand"] == "Gucci"]
        mock_db.get_sentiment_by_attributes.return_value = gucci_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?brand=Gucci")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["brand"] == "Gucci"
        assert data[0]["sentiment"] == "good"
        assert data[0]["product_name"] == "Ace Leather Sneaker"
        
        # Verify database call
        mock_db.get_sentiment_by_attributes.assert_called_once()
        call_args = mock_db.get_sentiment_by_attributes.call_args
        assert call_args[0][0] == "usr_test_001"  # user_id
        assert call_args[0][1]["brand"] == ["Gucci"]

    async def test_sentiment_by_multiple_brands(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test filtering sentiment by multiple brands"""
        mock_db.get_sentiment_by_attributes.return_value = sample_interactions
        
        # Make request with multiple brands
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?brand=Gucci&brand=Nike")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify database call
        mock_db.get_sentiment_by_attributes.assert_called_once()
        call_args = mock_db.get_sentiment_by_attributes.call_args
        assert call_args[0][1]["brand"] == ["Gucci", "Nike"]

    async def test_sentiment_by_style_tags(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test filtering sentiment by style tags"""
        # Mock database response - luxury items only
        luxury_interactions = [i for i in sample_interactions if "luxury" in i["attributes"].get("style_tags", [])]
        mock_db.get_sentiment_by_attributes.return_value = luxury_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?style_tags=luxury")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "luxury" in data[0]["attributes"]["style_tags"]
        assert data[0]["brand"] == "Gucci"
        
        # Verify database call
        call_args = mock_db.get_sentiment_by_attributes.call_args
        assert call_args[0][1]["style_tags"] == ["luxury"]

    async def test_sentiment_by_materials_and_colors(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test filtering sentiment by materials and colors"""
        # Mock database response - leather and white items
        leather_white_interactions = [
            i for i in sample_interactions 
            if "leather" in i["attributes"].get("materials", []) and "white" in i["attributes"].get("colors", [])
        ]
        mock_db.get_sentiment_by_attributes.return_value = leather_white_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?materials=leather&colors=white")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "leather" in data[0]["attributes"]["materials"]
        assert "white" in data[0]["attributes"]["colors"]
        
        # Verify database call
        call_args = mock_db.get_sentiment_by_attributes.call_args
        assert call_args[0][1]["materials"] == ["leather"]
        assert call_args[0][1]["colors"] == ["white"]

    async def test_sentiment_by_price_range(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test filtering sentiment by price range"""
        # Mock database response - expensive items only
        expensive_interactions = [i for i in sample_interactions if i["price"] >= 500]
        mock_db.get_sentiment_by_attributes.return_value = expensive_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?price_min=500&price_max=1000")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["price"] == 690.00
        assert data[0]["brand"] == "Gucci"
        
        # Verify database call
        call_args = mock_db.get_sentiment_by_attributes.call_args
        assert call_args[0][1]["price_min"] == 500
        assert call_args[0][1]["price_max"] == 1000

    async def test_sentiment_by_category_and_sub_category(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test filtering sentiment by category and sub_category"""
        # Mock database response - sneakers only
        sneaker_interactions = [
            i for i in sample_interactions 
            if i["category"] == "shoe" and i["sub_category"] == "sneaker"
        ]
        mock_db.get_sentiment_by_attributes.return_value = sneaker_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?category=shoe&sub_category=sneaker")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "shoe"
        assert data[0]["sub_category"] == "sneaker"
        
        # Verify database call
        call_args = mock_db.get_sentiment_by_attributes.call_args
        assert call_args[0][1]["category"] == "shoe"
        assert call_args[0][1]["sub_category"] == "sneaker"

    async def test_sentiment_by_good_sentiment_filter(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test filtering by good sentiment only"""
        # Mock database response - good sentiment only
        good_interactions = [i for i in sample_interactions if i["sentiment"] == "good"]
        mock_db.get_sentiment_by_attributes.return_value = good_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?sentiment=good&brand=Gucci")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sentiment"] == "good"
        assert data[0]["brand"] == "Gucci"
        
        # Verify database call
        call_args = mock_db.get_sentiment_by_attributes.call_args
        assert call_args[0][1]["sentiment"] == "good"
        assert call_args[0][1]["brand"] == ["Gucci"]

    async def test_sentiment_by_bad_sentiment_filter(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test filtering by bad sentiment only"""
        # Mock database response - bad sentiment only
        bad_interactions = [i for i in sample_interactions if i["sentiment"] == "bad"]
        mock_db.get_sentiment_by_attributes.return_value = bad_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?sentiment=bad")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sentiment"] == "bad"
        assert data[0]["brand"] == "Nike"
        
        # Verify database call
        call_args = mock_db.get_sentiment_by_attributes.call_args
        assert call_args[0][1]["sentiment"] == "bad"

    async def test_sentiment_by_use_cases(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test filtering sentiment by use cases"""
        # Mock database response - casual use case items
        casual_interactions = [
            i for i in sample_interactions 
            if "casual" in i["attributes"].get("use_cases", [])
        ]
        mock_db.get_sentiment_by_attributes.return_value = casual_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?use_cases=casual")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "casual" in data[0]["attributes"]["use_cases"]
        
        # Verify database call
        call_args = mock_db.get_sentiment_by_attributes.call_args
        assert call_args[0][1]["use_cases"] == ["casual"]

    async def test_sentiment_complex_filter_combination(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test complex combination of filters"""
        # Mock database response - specific combination
        mock_db.get_sentiment_by_attributes.return_value = []  # No matches for complex filter
        
        # Make request with multiple filters
        response = await test_client.get(
            "/read/user/usr_test_001/sentiment-by-attributes"
            "?brand=Gucci&style_tags=luxury&materials=leather&colors=white&sentiment=good&price_min=500"
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0  # No matches for this complex filter
        
        # Verify database call includes all filters
        call_args = mock_db.get_sentiment_by_attributes.call_args
        params = call_args[0][1]
        assert params["brand"] == ["Gucci"]
        assert params["style_tags"] == ["luxury"]
        assert params["materials"] == ["leather"]
        assert params["colors"] == ["white"]
        assert params["sentiment"] == "good"
        assert params["price_min"] == 500

    async def test_sentiment_with_pagination(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test sentiment by attributes with pagination"""
        mock_db.get_sentiment_by_attributes.return_value = sample_interactions[1:]  # Skip first
        
        # Make request with pagination
        response = await test_client.get(
            "/read/user/usr_test_001/sentiment-by-attributes?brand=Nike&limit=10&offset=1"
        )
        
        # Verify response
        assert response.status_code == 200
        
        # Verify database call includes pagination
        call_args = mock_db.get_sentiment_by_attributes.call_args
        params = call_args[0][1]
        assert params["limit"] == 10
        assert params["offset"] == 1
        assert params["brand"] == ["Nike"]

    async def test_sentiment_no_filters(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test sentiment by attributes with no filters (should return all user interactions)"""
        mock_db.get_sentiment_by_attributes.return_value = sample_interactions
        
        # Make request with no filters
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify database call
        call_args = mock_db.get_sentiment_by_attributes.call_args
        params = call_args[0][1]
        # Should only have pagination params
        assert params.get("limit") == 50
        assert params.get("offset") == 0

    async def test_sentiment_returns_full_product_details(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test that sentiment queries return full product details from JOIN"""
        mock_db.get_sentiment_by_attributes.return_value = sample_interactions[:1]
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/sentiment-by-attributes?brand=Gucci")
        
        # Verify response includes all product fields
        assert response.status_code == 200
        data = response.json()
        interaction = data[0]
        
        # Interaction fields
        assert "interaction_id" in interaction
        assert "sentiment" in interaction
        assert "sentiment_notes" in interaction
        
        # Product fields from JOIN
        assert "product_name" in interaction
        assert "brand" in interaction
        assert "category" in interaction
        assert "sub_category" in interaction
        assert "price" in interaction
        assert "currency" in interaction
        assert "size" in interaction
        assert "color" in interaction
        assert "material" in interaction
        assert "attributes" in interaction
        assert "product_url" in interaction
        assert "image_path" in interaction
        assert "product_summary" in interaction