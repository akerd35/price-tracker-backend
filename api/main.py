from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models.product import ProductResponse
from models.notification import NotificationResponse
from core.database import engine, Base, get_db
from repositories.product_repository import ProductRepository
from repositories.notification_repository import NotificationRepository

app = FastAPI(title="Price Tracker API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok", "message": "Backend is running smoothly!"}

@app.post("/api/v1/products", tags=["Products"], response_model=ProductResponse)
async def create_product(product: ProductResponse, db: AsyncSession = Depends(get_db)) -> ProductResponse:
    repo = ProductRepository(db)
    saved_product = await repo.save_product(product)
    return saved_product

@app.put("/api/v1/products/{product_id}", tags=["Products"], response_model=ProductResponse)
async def update_product(product_id: str, product: ProductResponse, db: AsyncSession = Depends(get_db)) -> ProductResponse:
    repo = ProductRepository(db)
    saved_product = await repo.save_product(product)
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

@app.delete("/api/v1/products/{product_id}", tags=["Products"])
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    repo = ProductRepository(db)
    success = await repo.delete_product(product_id)
    if success:
        return {"status": "success", "message": "Product deleted successfully"}
    return {"status": "error", "message": "Product not found"}

