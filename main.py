from __future__ import annotations

from dotenv import load_dotenv
from services import SearchService, ScraperService

load_dotenv()


def search_and_scrape(query: str, count: int = 10) -> list[dict]:
    """Search You.com and scrape products from the first result."""
    search = SearchService()
    scraper = ScraperService()

    results = search.search(query, count=count)
    web_results = results.get("results", {}).get("web", [])

    if not web_results:
        print("No search results found.")
        return []

    url = web_results[0]["url"]
    print(f"Scraping: {url}")
    return scraper.scrape_products(url)


if __name__ == "__main__":
    products = search_and_scrape("nike shoes size 10 men")

    if not products:
        print("No products found.")
    else:
        for idx, p in enumerate(products[:10], 1):
            print(f"{idx}. {p['title']}")
            print(f"   Price: {p.get('price') or 'N/A'}")
            print(f"   Image: {p.get('image') or 'N/A'}")
            print(f"   URL:   {p.get('url') or 'N/A'}\n")
