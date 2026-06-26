from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.db_models import Product
from models.product import ProductResponse
import datetime

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_product(self, product_data: ProductResponse) -> ProductResponse:
        stmt = select(Product).where(Product.store_url == product_data.storeUrl)
        result = await self.db.execute(stmt)
        existing_product = result.scalars().first()

        now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        if existing_product:
            existing_product.name = product_data.name
            existing_product.current_price = product_data.currentPrice
            existing_product.target_price = product_data.targetPrice
            existing_product.image_url = product_data.imageUrl
            existing_product.last_updated = now_utc
            await self.db.commit()
            await self.db.refresh(existing_product)
            return ProductResponse(
                id=existing_product.id,
                name=existing_product.name,
                storeUrl=existing_product.store_url,
                currentPrice=existing_product.current_price,
                targetPrice=existing_product.target_price,
                imageUrl=existing_product.image_url,
                lastUpdated=existing_product.last_updated.replace(tzinfo=datetime.timezone.utc) if existing_product.last_updated.tzinfo is None else existing_product.last_updated
            )
        else:
            new_product = Product(
                id=product_data.id,
                name=product_data.name,
                store_url=product_data.storeUrl,
                current_price=product_data.currentPrice,
                target_price=product_data.targetPrice,
                image_url=product_data.imageUrl,
                last_updated=now_utc
            )
            self.db.add(new_product)
            await self.db.commit()
            await self.db.refresh(new_product)
            return ProductResponse(
                id=new_product.id,
                name=new_product.name,
                storeUrl=new_product.store_url,
                currentPrice=new_product.current_price,
                targetPrice=new_product.target_price,
                imageUrl=new_product.image_url,
                lastUpdated=new_product.last_updated.replace(tzinfo=datetime.timezone.utc) if new_product.last_updated.tzinfo is None else new_product.last_updated
            )

    async def update_product_price(self, product_id: str, new_price: float) -> ProductResponse | None:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalars().first()
        
        if not product:
            return None
            
        product.current_price = new_price
        product.last_updated = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        await self.db.commit()
        await self.db.refresh(product)
        
        dt = product.last_updated
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
            
        return ProductResponse(
            id=product.id,
            name=product.name,
            storeUrl=product.store_url,
            currentPrice=product.current_price,
            targetPrice=product.target_price,
            imageUrl=product.image_url,
            lastUpdated=dt
        )
        
    async def clear_target_price(self, product_id: str) -> None:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalars().first()
        if product:
            product.target_price = None
            await self.db.commit()

    async def get_all_products(self) -> list[ProductResponse]:
        stmt = select(Product).order_by(Product.last_updated.desc())
        result = await self.db.execute(stmt)
        db_products = result.scalars().all()
        
        products = []
        for p in db_products:
            # Reconstruct datetime so Pydantic knows it's UTC (or native if we prefer)
            dt = p.last_updated
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
                
            products.append(ProductResponse(
                id=p.id,
                name=p.name,
                storeUrl=p.store_url,
                currentPrice=p.current_price,
                targetPrice=p.target_price,
                imageUrl=p.image_url,
                lastUpdated=dt
            ))
        return products

    async def delete_product(self, product_id: str) -> bool:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalars().first()
        if product:
            await self.db.delete(product)
            await self.db.commit()
            return True
        return False
