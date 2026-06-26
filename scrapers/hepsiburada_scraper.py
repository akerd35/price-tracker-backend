import uuid
import os
import urllib.parse
import html
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scrapers.base_scraper import BaseScraper
from models.product import ProductResponse

class HepsiburadaScraper(BaseScraper):
    async def fetch_data(self, url: str) -> ProductResponse:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        target_url = url
        scraper_api_key = os.getenv("SCRAPER_API_KEY")
        if scraper_api_key:
            target_url = f"http://api.scraperapi.com/?api_key={scraper_api_key}&url={urllib.parse.quote(url)}&render=true"
            
        async with AsyncSession(impersonate='chrome110') as client:
            response = await client.get(target_url, headers=headers)
            response.raise_for_status()
            html = response.text
            
        soup = BeautifulSoup(html, "lxml")
        
        title = "Hepsiburada Product"
        price = 0.0
        image_url = "https://via.placeholder.com/300"
        
        # Product Title
        title_tag = soup.select_one("h1[itemprop='name']") or soup.select_one(".product-name")
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"]
            elif soup.title:
                title = soup.title.get_text(strip=True)
                
        # Price extraction
        price_tag = soup.select_one("span[itemprop='price']") or soup.select_one(".price") or soup.find("meta", property="product:price:amount")
        
        if price_tag:
            if price_tag.name == "meta":
                price_text = price_tag.get("content", "0")
            else:
                price_text = price_tag.get("content") or price_tag.get_text(strip=True)
                
            clean_str = "".join(c for c in price_text if c.isdigit() or c in [',', '.'])
            if len(clean_str) > 3 and clean_str[-3] == ',':
                clean_str = clean_str[:-3].replace('.', '') + '.' + clean_str[-2:]
            elif len(clean_str) > 3 and clean_str[-3] == '.':
                clean_str = clean_str[:-3].replace(',', '') + '.' + clean_str[-2:]
            else:
                clean_str = clean_str.replace(',', '').replace('.', '')
            try:
                price = float(clean_str)
            except ValueError:
                price = 0.0
                
        # Image extraction
        img_tag = soup.select_one("img[itemprop='image']")
        if img_tag and img_tag.get("src"):
            image_url = img_tag["src"]
        else:
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                image_url = og_image["content"]
        
        if title:
            title = html.unescape(title)
                
        return ProductResponse(
            id=str(uuid.uuid4()),
            name=title[:255] if len(title) > 255 else title,
            storeUrl=url,
            currentPrice=price,
            targetPrice=None,
            imageUrl=image_url,
            lastUpdated=datetime.now(timezone.utc)
        )
