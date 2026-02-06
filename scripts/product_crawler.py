#!/usr/bin/env python3
"""
Product crawler using Playwright to extract product information from e-commerce sites.
Extracts data for the first 10 products from given URLs.
"""

import asyncio
import json
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Page


class ProductCrawler:
    def __init__(self):
        self.max_products = 10
        
    async def crawl_products(self, url: str) -> List[Dict]:
        """Crawl products from the given URL"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set user agent to avoid bot detection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                domain = urlparse(url).netloc.lower()
                if 'nike.com' in domain:
                    products = await self._crawl_nike(page, url)
                elif 'amazon.com' in domain:
                    products = await self._crawl_amazon(page, url)
                else:
                    print(f"Unsupported domain: {domain}")
                    return []
                    
                return products[:self.max_products]
                
            except Exception as e:
                print(f"Error crawling {url}: {e}")
                return []
            finally:
                await browser.close()
    
    async def _crawl_nike(self, page: Page, base_url: str) -> List[Dict]:
        """Crawl Nike products"""
        products = []
        
        # Wait for products to load
        await page.wait_for_selector('[data-testid="product-card"]', timeout=10000)
        
        # Get product cards
        product_cards = await page.query_selector_all('[data-testid="product-card"]')
        
        for i, card in enumerate(product_cards[:self.max_products]):
            try:
                product = await self._extract_nike_product(page, card, base_url)
                if product:
                    products.append(product)
                    print(f"Nike product {i+1}: {product['name']}")
            except Exception as e:
                print(f"Error extracting Nike product {i+1}: {e}")
                continue
                
        return products
    
    async def _extract_nike_product(self, page: Page, card, base_url: str) -> Optional[Dict]:
        """Extract product data from Nike product card"""
        try:
            # Product name - try multiple selectors
            name_elem = await card.query_selector('[data-testid="product-card__title"]')
            if not name_elem:
                name_elem = await card.query_selector('.product-card__title')
            if not name_elem:
                name_elem = await card.query_selector('h3, h2, .card-title')
            
            name = await name_elem.text_content() if name_elem else "Unknown Nike Product"
            name = name.strip() if name else "Unknown Nike Product"
            
            # Product URL
            link_elem = await card.query_selector('a')
            product_url = None
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    product_url = urljoin(base_url, href)
            
            # Price - try multiple selectors
            price_elem = await card.query_selector('[data-testid="product-price"]')
            if not price_elem:
                price_elem = await card.query_selector('.price, .product-price')
            price_text = await price_elem.text_content() if price_elem else None
            price = self._extract_price(price_text) if price_text else None
            
            # Image
            img_elem = await card.query_selector('img')
            image_url = await img_elem.get_attribute('src') if img_elem else None
            
            # Color info (sometimes in subtitle or description)
            subtitle_elem = await card.query_selector('[data-testid="product-card__subtitle"]')
            if not subtitle_elem:
                subtitle_elem = await card.query_selector('.product-card__subtitle, .subtitle')
            subtitle = await subtitle_elem.text_content() if subtitle_elem else ""
            
            return {
                'product_id': self._generate_id(name, 'nike'),
                'name': name,
                'brand': 'Nike',
                'category': 'shoe',
                'sub_category': 'sneaker',
                'price': price,
                'currency': 'USD',
                'size': None,
                'color': self._extract_color(subtitle),
                'material': None,
                'attributes': {
                    'subtitle': subtitle,
                    'original_url': product_url
                },
                'product_url': product_url,
                'image_path': image_url,
                'product_summary': f"{name} by Nike",
                'metadata': {
                    'source': 'nike.com',
                    'crawled_at': self._get_timestamp()
                }
            }
            
        except Exception as e:
            print(f"Error extracting Nike product: {e}")
            return None
    
    async def _crawl_amazon(self, page: Page, base_url: str) -> List[Dict]:
        """Crawl Amazon products"""
        products = []
        
        # Wait for search results - try multiple selectors
        try:
            await page.wait_for_selector('[data-component-type="s-search-result"]', timeout=15000)
        except:
            try:
                await page.wait_for_selector('.s-result-item', timeout=15000)
            except:
                print("Could not find Amazon product containers")
                return []
        
        # Get product containers - try multiple selectors
        product_containers = await page.query_selector_all('[data-component-type="s-search-result"]')
        if not product_containers:
            product_containers = await page.query_selector_all('.s-result-item')
        
        for i, container in enumerate(product_containers[:self.max_products]):
            try:
                product = await self._extract_amazon_product(page, container, base_url)
                if product:
                    products.append(product)
                    print(f"Amazon product {i+1}: {product['name']}")
            except Exception as e:
                print(f"Error extracting Amazon product {i+1}: {e}")
                continue
                
        return products
    
    async def _extract_amazon_product(self, page: Page, container, base_url: str) -> Optional[Dict]:
        """Extract product data from Amazon product container"""
        try:
            # Product name
            name_elem = await container.query_selector('h2 a span, [data-cy="title-recipe-title"] span')
            name = await name_elem.text_content() if name_elem else None
            
            # Product URL
            link_elem = await container.query_selector('h2 a')
            product_url = None
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    product_url = urljoin(base_url, href)
            
            # Price
            price_elem = await container.query_selector('.a-price-whole, .a-price .a-offscreen')
            price_text = await price_elem.text_content() if price_elem else None
            price = self._extract_price(price_text) if price_text else None
            
            # Image
            img_elem = await container.query_selector('img')
            image_url = await img_elem.get_attribute('src') if img_elem else None
            
            # Brand (sometimes available in title or separate element)
            brand = self._extract_brand_from_title(name) if name else None
            
            # Rating (for attributes)
            rating_elem = await container.query_selector('.a-icon-alt')
            rating_text = await rating_elem.get_attribute('textContent') if rating_elem else None
            
            return {
                'product_id': self._generate_id(name, 'amazon'),
                'name': name,
                'brand': brand,
                'category': 'shoe',
                'sub_category': 'sneaker',
                'price': price,
                'currency': 'USD',
                'size': None,
                'color': self._extract_color(name),
                'material': None,
                'attributes': {
                    'rating': rating_text,
                    'original_url': product_url
                },
                'product_url': product_url,
                'image_path': image_url,
                'product_summary': f"{name}",
                'metadata': {
                    'source': 'amazon.com',
                    'crawled_at': self._get_timestamp()
                }
            }
            
        except Exception as e:
            print(f"Error extracting Amazon product: {e}")
            return None
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from price text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract number
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group())
            except ValueError:
                pass
        return None
    
    def _extract_color(self, text: str) -> Optional[str]:
        """Extract color from product text"""
        if not text:
            return None
            
        colors = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'brown', 'gray', 'grey', 
                  'pink', 'purple', 'orange', 'navy', 'beige', 'tan', 'silver', 'gold']
        
        text_lower = text.lower()
        for color in colors:
            if color in text_lower:
                return color.title()
        return None
    
    def _extract_brand_from_title(self, title: str) -> Optional[str]:
        """Extract brand from product title"""
        if not title:
            return None
            
        brands = ['nike', 'adidas', 'puma', 'reebok', 'new balance', 'converse', 
                  'vans', 'under armour', 'asics', 'skechers']
        
        title_lower = title.lower()
        for brand in brands:
            if brand in title_lower:
                return brand.title()
        return None
    
    def _generate_id(self, name: str, source: str) -> str:
        """Generate a simple product ID"""
        if not name:
            name = "unknown"
        # Simple hash-like ID
        import hashlib
        return hashlib.md5(f"{source}_{name}".encode()).hexdigest()[:12]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


async def test_crawler():
    """Test the crawler with the specified URLs"""
    crawler = ProductCrawler()
    
    test_urls = [
        "https://www.nike.com/w/mens-training-gym-shoes-58jtoznik1zy7ok",
        "https://www.amazon.com/white-sneakers-men/s?k=white+sneakers+men"
    ]
    
    all_products = []
    
    for url in test_urls:
        print(f"\n{'='*50}")
        print(f"Crawling: {url}")
        print(f"{'='*50}")
        
        products = await crawler.crawl_products(url)
        all_products.extend(products)
        
        print(f"\nExtracted {len(products)} products:")
        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product['name']}")
            print(f"   Brand: {product['brand']}")
            print(f"   Price: ${product['price']}" if product['price'] else "   Price: N/A")
            print(f"   Color: {product['color']}" if product['color'] else "   Color: N/A")
            print(f"   URL: {product['product_url']}")
            print(f"   Image: {product['image_path']}")
    
    print(f"\n{'='*50}")
    print(f"Total products extracted: {len(all_products)}")
    print(f"{'='*50}")
    
    # Save results to JSON for inspection
    with open('/Users/aq_home/1Projects/TalkShop/scripts/crawled_products.json', 'w') as f:
        json.dump(all_products, f, indent=2)
    
    print(f"Results saved to: scripts/crawled_products.json")
    
    return all_products


def simulate_database_insertion(products: List[Dict]) -> None:
    """Simulate inserting products into the database"""
    print("\n" + "="*60)
    print("SIMULATING DATABASE INSERTION")
    print("="*60)
    
    for i, product in enumerate(products, 1):
        print(f"\nINSERT INTO products (")
        print(f"  product_id, name, brand, category, sub_category,")
        print(f"  price, currency, size, color, material,")
        print(f"  attributes, product_url, image_path, product_summary, metadata")
        print(f") VALUES (")
        print(f"  '{product['product_id']}',")
        print(f"  '{product['name']}',")
        print(f"  '{product['brand']}',")
        print(f"  '{product['category']}',")
        print(f"  '{product['sub_category']}',")
        print(f"  {product['price']},")
        print(f"  '{product['currency']}',")
        print(f"  {product['size']},")
        print(f"  {product['color']},")
        print(f"  {product['material']},")
        print(f"  '{json.dumps(product['attributes'])}',")
        print(f"  '{product['product_url']}',")
        print(f"  '{product['image_path']}',")
        print(f"  '{product['product_summary']}',")
        print(f"  '{json.dumps(product['metadata'])}'")
        print(f");")
        
        if i >= 3:  # Only show first 3 for brevity
            print(f"\n... ({len(products) - 3} more products)")
            break


async def main():
    """Main function"""
    products = await test_crawler()
    
    # Simulate database insertion
    if products:
        simulate_database_insertion(products)
    
    return products


if __name__ == "__main__":
    asyncio.run(main())