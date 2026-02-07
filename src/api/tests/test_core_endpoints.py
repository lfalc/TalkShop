import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock


@pytest.mark.asyncio
class TestCoreEndpoints:
    """Test core user and product endpoints"""

    async def test_get_user_success(self, test_client: AsyncClient, mock_db: AsyncMock, sample_user_profile):
        """Test successful user retrieval"""
        # Mock database response
        mock_db.get_user_profile.return_value = sample_user_profile
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "usr_test_001"
        assert data["gender"] == "female"
        assert "products" in data
        assert data["total_selections"] == 39
        
        # Verify database call
        mock_db.get_user_profile.assert_called_once_with("usr_test_001")

    async def test_get_user_not_found(self, test_client: AsyncClient, mock_db: AsyncMock):
        """Test user not found scenario"""
        # Mock database response
        mock_db.get_user_profile.return_value = None
        
        # Make request
        response = await test_client.get("/read/user/nonexistent_user")
        
        # Verify response
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_get_product_success(self, test_client: AsyncClient, mock_db: AsyncMock, sample_products):
        """Test successful product retrieval"""
        # Mock database response
        mock_db.get_product.return_value = sample_products[0]
        
        # Make request
        response = await test_client.get("/read/product/prd_gucci_sneaker_001")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == "prd_gucci_sneaker_001"
        assert data["name"] == "Ace Leather Sneaker"
        assert data["brand"] == "Gucci"
        assert data["category"] == "shoe"
        assert data["price"] == 690.00
        assert "attributes" in data
        
        # Verify database call
        mock_db.get_product.assert_called_once_with("prd_gucci_sneaker_001")

    async def test_get_product_not_found(self, test_client: AsyncClient, mock_db: AsyncMock):
        """Test product not found scenario"""
        # Mock database response
        mock_db.get_product.return_value = None
        
        # Make request
        response = await test_client.get("/read/product/nonexistent_product")
        
        # Verify response
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    async def test_get_user_interactions_all(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test getting all user interactions"""
        # Mock database response
        mock_db.get_user_interactions.return_value = sample_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/interactions")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify first interaction has both interaction and product data
        interaction = data[0]
        assert interaction["user_id"] == "usr_test_001"
        assert interaction["sentiment"] == "good"
        assert interaction["product_name"] == "Ace Leather Sneaker"
        assert interaction["brand"] == "Gucci"
        assert "attributes" in interaction
        
        # Verify database call
        mock_db.get_user_interactions.assert_called_once_with(
            user_id="usr_test_001",
            sentiment=None,
            limit=50,
            offset=0
        )

    async def test_get_user_interactions_filtered_by_sentiment(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test getting user interactions filtered by sentiment"""
        # Mock database response - only good sentiment
        good_interactions = [i for i in sample_interactions if i["sentiment"] == "good"]
        mock_db.get_user_interactions.return_value = good_interactions
        
        # Make request
        response = await test_client.get("/read/user/usr_test_001/interactions?sentiment=good")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sentiment"] == "good"
        assert data[0]["product_name"] == "Ace Leather Sneaker"
        
        # Verify database call
        mock_db.get_user_interactions.assert_called_once_with(
            user_id="usr_test_001",
            sentiment="good",
            limit=50,
            offset=0
        )

    async def test_get_user_interactions_with_pagination(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test user interactions with pagination parameters"""
        # Mock database response
        mock_db.get_user_interactions.return_value = sample_interactions[1:]  # Skip first item
        
        # Make request with pagination
        response = await test_client.get("/read/user/usr_test_001/interactions?limit=10&offset=1")
        
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

    async def test_get_product_interactions(self, test_client: AsyncClient, mock_db: AsyncMock, sample_interactions):
        """Test getting product interactions"""
        # Mock database response - interactions for specific product
        product_interactions = [i for i in sample_interactions if i["product_id"] == "prd_gucci_sneaker_001"]
        mock_db.get_product_interactions.return_value = product_interactions
        
        # Make request
        response = await test_client.get("/read/product/prd_gucci_sneaker_001/interactions")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["product_id"] == "prd_gucci_sneaker_001"
        assert data[0]["sentiment"] == "good"
        assert data[0]["product_name"] == "Ace Leather Sneaker"
        
        # Verify database call
        mock_db.get_product_interactions.assert_called_once_with(
            product_id="prd_gucci_sneaker_001",
            sentiment=None,
            limit=50,
            offset=0
        )

    async def test_get_product_interactions_bad_sentiment(self, test_client: AsyncClient, mock_db: AsyncMock):
        """Test getting product interactions with bad sentiment filter"""
        # Mock database response - no bad interactions for this product
        mock_db.get_product_interactions.return_value = []
        
        # Make request
        response = await test_client.get("/read/product/prd_gucci_sneaker_001/interactions?sentiment=bad")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        
        # Verify database call
        mock_db.get_product_interactions.assert_called_once_with(
            product_id="prd_gucci_sneaker_001",
            sentiment="bad",
            limit=50,
            offset=0
        )

    async def test_health_check(self, test_client: AsyncClient):
        """Test health check endpoint"""
        response = await test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    async def test_root_endpoint(self, test_client: AsyncClient):
        """Test root endpoint"""
        response = await test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "TalkShop API"
        assert "version" in data