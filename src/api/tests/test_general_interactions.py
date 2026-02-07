import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock


@pytest.mark.asyncio
class TestGeneralInteractions:
    """Test general interactions endpoint functionality"""

    async def test_get_interactions_by_user_and_product(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test getting specific user-product interaction"""
        # Mock database response - specific interaction
        specific_interaction = [i for i in sample_interactions if i["product_id"] == "prd_gucci_sneaker_001"]
        mock_db.get_user_interactions.return_value = sample_interactions
        
        # Make request
        response = await test_client.get(
            "/read/interactions?user_id=usr_test_001&product_id=prd_gucci_sneaker_001"
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == "usr_test_001"
        assert data[0]["product_id"] == "prd_gucci_sneaker_001"
        
        # Verify database call
        mock_db.get_user_interactions.assert_called_once_with(
            user_id="usr_test_001",
            sentiment=None,
            limit=50,
            offset=0
        )

    async def test_get_interactions_by_user_only(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test getting interactions for a specific user"""
        mock_db.get_user_interactions.return_value = sample_interactions
        
        # Make request
        response = await test_client.get("/read/interactions?user_id=usr_test_001")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(i["user_id"] == "usr_test_001" for i in data)
        
        # Verify database call
        mock_db.get_user_interactions.assert_called_once_with(
            user_id="usr_test_001",
            sentiment=None,
            limit=50,
            offset=0
        )

    async def test_get_interactions_by_product_only(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test getting interactions for a specific product"""
        product_interactions = [i for i in sample_interactions if i["product_id"] == "prd_gucci_sneaker_001"]
        mock_db.get_product_interactions.return_value = product_interactions
        
        # Make request
        response = await test_client.get("/read/interactions?product_id=prd_gucci_sneaker_001")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["product_id"] == "prd_gucci_sneaker_001"
        
        # Verify database call
        mock_db.get_product_interactions.assert_called_once_with(
            product_id="prd_gucci_sneaker_001",
            sentiment=None,
            limit=50,
            offset=0
        )

    async def test_get_interactions_with_sentiment_filter(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test getting interactions with sentiment filter"""
        good_interactions = [i for i in sample_interactions if i["sentiment"] == "good"]
        mock_db.get_user_interactions.return_value = good_interactions
        
        # Make request
        response = await test_client.get("/read/interactions?user_id=usr_test_001&sentiment=good")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sentiment"] == "good"
        
        # Verify database call
        mock_db.get_user_interactions.assert_called_once_with(
            user_id="usr_test_001",
            sentiment="good",
            limit=50,
            offset=0
        )

    async def test_get_interactions_no_parameters(self, test_client: AsyncClient, mock_db: AsyncMock):
        """Test getting interactions with no parameters (should return empty list)"""
        # Make request with no parameters
        response = await test_client.get("/read/interactions")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        assert data == []
        
        # Verify no database calls were made
        mock_db.get_user_interactions.assert_not_called()
        mock_db.get_product_interactions.assert_not_called()

    async def test_get_interactions_with_pagination(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test getting interactions with pagination parameters"""
        mock_db.get_user_interactions.return_value = sample_interactions[1:]  # Skip first
        
        # Make request with pagination
        response = await test_client.get("/read/interactions?user_id=usr_test_001&limit=10&offset=1")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Verify database call with pagination
        mock_db.get_user_interactions.assert_called_once_with(
            user_id="usr_test_001",
            sentiment=None,
            limit=10,
            offset=1
        )

    async def test_get_interactions_returns_full_product_details(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test that interactions endpoint returns full product details from JOIN"""
        mock_db.get_user_interactions.return_value = sample_interactions[:1]
        
        # Make request
        response = await test_client.get("/read/interactions?user_id=usr_test_001")
        
        # Verify response includes all fields
        assert response.status_code == 200
        data = response.json()
        interaction = data[0]
        
        # Interaction fields
        assert "interaction_id" in interaction
        assert "user_id" in interaction
        assert "product_id" in interaction
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