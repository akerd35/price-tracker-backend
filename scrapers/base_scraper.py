from abc import ABC, abstractmethod
from models.product import ProductResponse

class BaseScraper(ABC):
    @abstractmethod
    async def fetch_data(self, url: str) -> ProductResponse:
        pass
