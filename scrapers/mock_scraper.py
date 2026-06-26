import asyncio
import uuid
import random
from datetime import datetime, timezone
from scrapers.base_scraper import BaseScraper
from models.product import ProductResponse

class MockScraper(BaseScraper):
    async def fetch_data(self, url: str) -> ProductResponse:
        # Simulate network delay as per guidelines
        await asyncio.sleep(1.5)
        
        product_id = str(uuid.uuid4())
        mock_prices = [199.99, 499.00, 899.50, 1299.99, 49.99]
        mock_names = [
            "Sony WH-1000XM5 Wireless Headphones",
            "Apple iPad Air (5th Generation)",
            "Samsung Galaxy S24 Ultra",
            "Nintendo Switch OLED Model",
            "Logitech MX Master 3S Wireless Mouse"
        ]
        
        current_price = random.choice(mock_prices)
        
        return ProductResponse(
            id=product_id,
            name=random.choice(mock_names),
            storeUrl=url,
            currentPrice=current_price,
            targetPrice=round(current_price * 0.9, 2),
            imageUrl="https://via.placeholder.com/300",
            lastUpdated=datetime.now(timezone.utc)
        )
