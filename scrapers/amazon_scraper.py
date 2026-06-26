import uuid
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scrapers.base_scraper import BaseScraper
from models.product import ProductResponse

class AmazonScraper(BaseScraper):
    async def fetch_data(self, url: str) -> ProductResponse:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7",
        }
        
        async with AsyncSession(impersonate='chrome110') as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            html = response.text
            
        soup = BeautifulSoup(html, "lxml")
        
        title = "Amazon Product"
        price = 0.0
        image_url = "https://via.placeholder.com/300"
        
        # Product Title
        title_tag = soup.select_one("#productTitle")
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"]
            elif soup.title:
                title = soup.title.get_text(strip=True)
                
        # Price extraction
        price_selectors = [
            ".a-price .a-offscreen", 
            "#priceblock_ourprice", 
            "#priceblock_dealprice", 
            ".a-color-price"
        ]
        
        price_text = ""
        for selector in price_selectors:
            price_tag = soup.select_one(selector)
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                break
                
        if price_text:
            clean_str = "".join(c for c in price_text if c.isdigit() or c in [',', '.'])
            if len(clean_str) > 3 and clean_str[-3] in [',', '.']:
                clean_str = clean_str[:-3].replace(',', '').replace('.', '') + '.' + clean_str[-2:]
            else:
                clean_str = clean_str.replace(',', '').replace('.', '')
            try:
                price = float(clean_str)
            except ValueError:
                price = 0.0
                
        # Image extraction
        img_tag = soup.select_one("#landingImage")
        if img_tag and img_tag.get("src"):
            image_url = img_tag["src"]
        else:
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                image_url = og_image["content"]
                
        return ProductResponse(
            id=str(uuid.uuid4()),
            name=title,
            storeUrl=url,
            currentPrice=price,
            targetPrice=None,
            imageUrl=image_url,
            lastUpdated=datetime.now(timezone.utc)
        )
