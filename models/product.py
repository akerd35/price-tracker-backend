from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductResponse(BaseModel):
    id: str
    name: str
    storeUrl: str
    currentPrice: float
    targetPrice: Optional[float] = None
    imageUrl: str
    lastUpdated: datetime

class ExtractRequest(BaseModel):
    url: str
