from fastapi import FastAPI, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models.product import ExtractRequest, ProductResponse
from models.notification import NotificationResponse
from services.url_service import UrlService
from core.database import engine, Base, get_db
from repositories.product_repository import ProductRepository
from repositories.notification_repository import NotificationRepository
from services.scheduler_service import start_scheduler, stop_scheduler

app = FastAPI(title="Price Tracker API", version="1.0.0")
url_service = UrlService()

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok", "message": "Backend is running smoothly!"}

@app.post("/api/v1/products/extract", tags=["Products"], response_model=ProductResponse)
async def extract_product(request: ExtractRequest, db: AsyncSession = Depends(get_db)) -> ProductResponse:
    product_data = await url_service.extract_product(request.url)
    repo = ProductRepository(db)
    saved_product = await repo.save_product(product_data)
    return saved_product

@app.get("/api/v1/products", tags=["Products"], response_model=List[ProductResponse])
async def get_all_products(db: AsyncSession = Depends(get_db)) -> List[ProductResponse]:
    repo = ProductRepository(db)
    products = await repo.get_all_products()
    return products

@app.get("/api/v1/notifications", tags=["Notifications"], response_model=List[NotificationResponse])
async def get_notifications(db: AsyncSession = Depends(get_db)) -> List[NotificationResponse]:
    repo = NotificationRepository(db)
    notifications = await repo.get_all_notifications()
    return notifications
