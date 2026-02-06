import re
import json
import requests
from bs4 import BeautifulSoup


class ScraperService:
    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def scrape_products(self, url: str) -> list[dict]:
        """Scrape product info (title, price, image) from a given URL."""
        resp = requests.get(
            url,
            headers={"User-Agent": self.USER_AGENT},
            timeout=30,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        products = self._extract_jsonld(soup)
        if products:
            return products

        return self._extract_html(soup)

    # -- JSON-LD extraction --------------------------------------------------

    def _extract_jsonld(self, soup: BeautifulSoup) -> list[dict]:
        products = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") == "Product":
                        products.append(self._parse_jsonld_product(item))
                    for member in item.get("itemListElement", []):
                        inner = member.get("item", member)
                        if inner.get("@type") == "Product":
                            products.append(self._parse_jsonld_product(inner))
            except (json.JSONDecodeError, TypeError):
                continue
        return products

    @staticmethod
    def _parse_jsonld_product(item: dict) -> dict:
        price = None
        offers = item.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        if offers:
            price = offers.get("price") or offers.get("lowPrice")
            currency = offers.get("priceCurrency", "")
            if price:
                price = f"{currency} {price}".strip()

        image = item.get("image", "")
        if isinstance(image, list):
            image = image[0] if image else ""
        if isinstance(image, dict):
            image = image.get("url", "")

        return {
            "title": item.get("name", ""),
            "price": price,
            "image": image,
            "url": item.get("url", ""),
        }

    # -- HTML fallback extraction ---------------------------------------------

    def _extract_html(self, soup: BeautifulSoup) -> list[dict]:
        card_selectors = [
            "[data-component='product-card']",
            ".product-card",
            ".product-tile",
            ".product-grid__item",
            ".s-result-item[data-asin]",
            ".product-item",
            ".grid-item",
        ]
        cards = []
        for sel in card_selectors:
            cards = soup.select(sel)
            if cards:
                break

        products = []
        for card in cards:
            title = self._text(card, [
                "[data-component='product-title']", ".product-title",
                ".product-card__title", ".product-name", "h2 a", "h3 a",
                "h2", "h3", ".title", "[class*='title']",
            ])
            if not title:
                continue

            price = self._text(card, [
                "[data-component='product-price']", ".product-price",
                ".price", ".product-card__price", "[class*='price']",
                "span.a-price > span.a-offscreen",
            ])
            image = self._attr(card, "img", "src") or self._attr(card, "img", "data-src")
            link = self._attr(card, "a", "href")

            products.append({
                "title": title.strip(),
                "price": re.sub(r"\s+", " ", price).strip() if price else None,
                "image": image,
                "url": link,
            })

        return products

    # -- helpers --------------------------------------------------------------

    @staticmethod
    def _text(parent, selectors: list[str]) -> str | None:
        for sel in selectors:
            el = parent.select_one(sel)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)
        return None

    @staticmethod
    def _attr(parent, selector: str, attr: str) -> str | None:
        el = parent.select_one(selector)
        if el and el.get(attr):
            return el[attr]
        return None
