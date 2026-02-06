import pytest
import pytest_asyncio
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_search_returns_products(client):
    """POST /search returns scraped products from top search result."""
    mock_search_response = {
        "results": {
            "web": [
                {"url": "https://www.nike.com/w/mens-shoes", "title": "Nike Shoes"}
            ]
        }
    }
    mock_scraped = [
        {"title": "Air Max 90", "price": "$120.00", "image": "https://img.com/1.jpg", "url": "https://nike.com/air-max-90"},
        {"title": "Air Force 1", "price": "$110.00", "image": "https://img.com/2.jpg", "url": "https://nike.com/air-force-1"},
    ]

    with patch("api.main.SearchService") as MockSearch, \
         patch("api.main.ScraperService") as MockScraper:
        MockSearch.return_value.search.return_value = mock_search_response
        MockScraper.return_value.scrape_products.return_value = mock_scraped

        response = await client.post("/search", json={"query": "nike shoes size 10 men"})

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "nike shoes size 10 men"
    assert data["source_url"] == "https://www.nike.com/w/mens-shoes"
    assert len(data["products"]) == 2
    assert data["products"][0]["title"] == "Air Max 90"
    assert data["products"][0]["price"] == "$120.00"


@pytest.mark.asyncio
async def test_search_no_web_results(client):
    """POST /search returns empty products when no web results found."""
    mock_search_response = {"results": {"web": []}}

    with patch("api.main.SearchService") as MockSearch:
        MockSearch.return_value.search.return_value = mock_search_response

        response = await client.post("/search", json={"query": "nonexistent product xyz"})

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "nonexistent product xyz"
    assert data["source_url"] is None
    assert data["products"] == []


@pytest.mark.asyncio
async def test_search_empty_query_rejected(client):
    """POST /search rejects empty query."""
    response = await client.post("/search", json={"query": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_custom_count(client):
    """POST /search passes count parameter to search service."""
    mock_search_response = {"results": {"web": []}}

    with patch("api.main.SearchService") as MockSearch:
        MockSearch.return_value.search.return_value = mock_search_response

        response = await client.post("/search", json={"query": "shoes", "count": 5})

    assert response.status_code == 200
    MockSearch.return_value.search.assert_called_once_with("shoes", count=5)


@pytest.mark.asyncio
async def test_search_service_failure(client):
    """POST /search returns 502 when search service fails."""
    with patch("api.main.SearchService") as MockSearch:
        MockSearch.return_value.search.side_effect = Exception("API timeout")

        response = await client.post("/search", json={"query": "nike shoes"})

    assert response.status_code == 502
    assert "Search service unavailable" in response.json()["detail"]


@pytest.mark.asyncio
async def test_scraper_failure(client):
    """POST /search returns 502 when scraping fails."""
    mock_search_response = {
        "results": {
            "web": [{"url": "https://example.com/products", "title": "Products"}]
        }
    }

    with patch("api.main.SearchService") as MockSearch, \
         patch("api.main.ScraperService") as MockScraper:
        MockSearch.return_value.search.return_value = mock_search_response
        MockScraper.return_value.scrape_products.side_effect = Exception("Connection refused")

        response = await client.post("/search", json={"query": "shoes"})

    assert response.status_code == 502
    assert "Failed to scrape" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_products_with_missing_fields(client):
    """POST /search handles products with optional fields missing."""
    mock_search_response = {
        "results": {
            "web": [{"url": "https://example.com", "title": "Example"}]
        }
    }
    mock_scraped = [
        {"title": "Basic Product", "price": None, "image": None, "url": None},
    ]

    with patch("api.main.SearchService") as MockSearch, \
         patch("api.main.ScraperService") as MockScraper:
        MockSearch.return_value.search.return_value = mock_search_response
        MockScraper.return_value.scrape_products.return_value = mock_scraped

        response = await client.post("/search", json={"query": "products"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 1
    assert data["products"][0]["title"] == "Basic Product"
    assert data["products"][0]["price"] is None


@pytest.mark.asyncio
async def test_search_raw_returns_raw_results(client):
    """POST /search with raw=true returns raw You.com results without scraping."""
    mock_search_response = {
        "results": {
            "web": [
                {"url": "https://www.nike.com/shoes", "title": "Nike Shoes", "description": "Shop Nike"},
                {"url": "https://www.adidas.com/shoes", "title": "Adidas Shoes", "description": "Shop Adidas"},
            ]
        }
    }

    with patch("api.main.SearchService") as MockSearch:
        MockSearch.return_value.search.return_value = mock_search_response

        response = await client.post("/search", json={"query": "shoes", "raw": True})

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "shoes"
    assert data["raw"] is True
    assert data["products"] == []
    assert data["source_url"] is None
    assert len(data["raw_results"]) == 2
    assert data["raw_results"][0]["url"] == "https://www.nike.com/shoes"
    assert data["raw_results"][1]["title"] == "Adidas Shoes"


@pytest.mark.asyncio
async def test_search_raw_empty_results(client):
    """POST /search with raw=true returns empty raw_results when no results."""
    mock_search_response = {"results": {"web": []}}

    with patch("api.main.SearchService") as MockSearch:
        MockSearch.return_value.search.return_value = mock_search_response

        response = await client.post("/search", json={"query": "nothing", "raw": True})

    assert response.status_code == 200
    data = response.json()
    assert data["raw"] is True
    assert data["raw_results"] == []


@pytest.mark.asyncio
async def test_search_raw_false_still_scrapes(client):
    """POST /search with raw=false (default) scrapes as before."""
    mock_search_response = {
        "results": {
            "web": [{"url": "https://example.com", "title": "Example"}]
        }
    }
    mock_scraped = [{"title": "Product A", "price": "$50", "image": None, "url": None}]

    with patch("api.main.SearchService") as MockSearch, \
         patch("api.main.ScraperService") as MockScraper:
        MockSearch.return_value.search.return_value = mock_search_response
        MockScraper.return_value.scrape_products.return_value = mock_scraped

        response = await client.post("/search", json={"query": "product", "raw": False})

    assert response.status_code == 200
    data = response.json()
    assert data["raw"] is False
    assert data["raw_results"] is None
    assert len(data["products"]) == 1
    assert data["source_url"] == "https://example.com"
