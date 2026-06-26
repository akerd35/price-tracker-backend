from urllib.parse import urlparse
from models.product import ProductResponse
from scrapers.mock_scraper import MockScraper
from scrapers.amazon_scraper import AmazonScraper
from scrapers.hepsiburada_scraper import HepsiburadaScraper
from scrapers.universal_scraper import UniversalScraper

class UrlService:
    def __init__(self) -> None:
        self.mock_scraper = MockScraper()
        self.amazon_scraper = AmazonScraper()
        self.hepsiburada_scraper = HepsiburadaScraper()
        self.universal_scraper = UniversalScraper()
        
    async def extract_product(self, url: str) -> ProductResponse:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        if "amazon" in domain:
            return await self.amazon_scraper.fetch_data(url)
        elif "hepsiburada" in domain:
            return await self.hepsiburada_scraper.fetch_data(url)
        else:
            return await self.universal_scraper.fetch_data(url)
