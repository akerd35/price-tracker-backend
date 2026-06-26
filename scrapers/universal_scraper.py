import uuid
import json
import os
import urllib.parse
import html
import re
import httpx
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scrapers.base_scraper import BaseScraper
from models.product import ProductResponse

class UniversalScraper(BaseScraper):
    async def fetch_data(self, url: str) -> ProductResponse:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7",
        }
        
        target_url = url
        scraper_api_key = os.getenv("SCRAPER_API_KEY")
        if scraper_api_key:
            target_url = f"http://api.scraperapi.com/?api_key={scraper_api_key}&url={urllib.parse.quote(url)}&render=true&premium=true"
            async with httpx.AsyncClient(timeout=90.0) as client:
                try:
                    response = await client.get(target_url, headers=headers)
                    response.raise_for_status()
                    html_content = response.text
                except Exception as e:
                    html_content = ""
                    print(f"UniversalScraper error fetching {target_url} via httpx: {e}")
        else:
            async with AsyncSession(impersonate='chrome110') as client:
                try:
                    response = await client.get(target_url, headers=headers, timeout=90)
                    response.raise_for_status()
                    html_content = response.text
                except Exception as e:
                    html_content = ""
                    print(f"UniversalScraper error fetching {target_url}: {e}")
            
        soup = BeautifulSoup(html_content, "lxml")
        
        title = "Unknown Product"
        price = 0.0
        image_url = "https://via.placeholder.com/300"
        
        # 1. Parse JSON-LD
        json_ld_data = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.get_text(strip=True))
                if isinstance(data, list):
                    json_ld_data.extend(data)
                else:
                    json_ld_data.append(data)
            except Exception:
                continue
                
        def extract_from_json_ld(data, key):
            if isinstance(data, dict):
                if key in data:
                    return data[key]
                for v in data.values():
                    res = extract_from_json_ld(v, key)
                    if res is not None:
                        return res
            elif isinstance(data, list):
                for item in data:
                    res = extract_from_json_ld(item, key)
                    if res is not None:
                        return res
            return None

        # Extract Title
        ld_title = extract_from_json_ld(json_ld_data, "name")
        if ld_title and isinstance(ld_title, str):
            title = ld_title
        else:
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"]
            elif soup.title:
                title = soup.title.get_text(strip=True)
                
        # Extract Price
        ld_price = extract_from_json_ld(json_ld_data, "price")
        if ld_price is not None:
            try:
                price = float(str(ld_price).replace(',', '.'))
            except ValueError:
                pass
                
        if price == 0.0:
            price_meta = soup.find("meta", property="product:price:amount") or soup.find("meta", property="og:price:amount")
            if price_meta and price_meta.get("content"):
                try:
                    price = float(price_meta["content"].replace(',', '.'))
                except ValueError:
                    pass
                    
        # Extract Image
        ld_image = extract_from_json_ld(json_ld_data, "image")
        if ld_image:
            if isinstance(ld_image, str):
                image_url = ld_image
            elif isinstance(ld_image, list) and len(ld_image) > 0 and isinstance(ld_image[0], str):
                image_url = ld_image[0]
            elif isinstance(ld_image, dict) and "url" in ld_image:
                image_url = ld_image["url"]
        
        if image_url == "https://via.placeholder.com/300":
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                image_url = og_image["content"]

        if title:
            title = html.unescape(title)

        # Fallback CSS Selectors for Price
        if price == 0.0:
            price_selectors = [
                ".prc-dsc", # Trendyol
                "[data-test-id='price']", # Hepsiburada
                ".product-list__price", # Vatan (list)
                ".product-detail-price", # Vatan (detail)
                ".product-price",
                ".price",
                "#offering-price"
            ]
            for selector in price_selectors:
                price_tag = soup.select_one(selector)
                if price_tag:
                    price_text = price_tag.get_text(strip=True)
                    # Extract digits, comma, dot
                    clean_text = re.sub(r'[^\d,.]', '', price_text)
                    if clean_text:
                        # Fix Turkish formatting (e.g. 5.699,00 -> 5699.00)
                        if ',' in clean_text and '.' in clean_text:
                            clean_text = clean_text.replace('.', '').replace(',', '.')
                        elif ',' in clean_text:
                            clean_text = clean_text.replace(',', '.')
                        
                        try:
                            price = float(clean_text)
                            if price > 0:
                                break
                        except ValueError:
                            pass

        return ProductResponse(
            id=str(uuid.uuid4()),
            name=title[:255] if len(title) > 255 else title, # Prevent too long titles
            storeUrl=url,
            currentPrice=price,
            targetPrice=None,
            imageUrl=image_url,
            lastUpdated=datetime.now(timezone.utc)
        )
