from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.database import SessionLocal
from repositories.product_repository import ProductRepository
from repositories.notification_repository import NotificationRepository
from services.url_service import UrlService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_prices_job():
    logger.info("Fiyatlar kontrol ediliyor...")
    async with SessionLocal() as db:
        repo = ProductRepository(db)
        notif_repo = NotificationRepository(db)
        url_service = UrlService()
        
        products = await repo.get_all_products()
        if not products:
            logger.info("Veritabanında takip edilen ürün bulunamadı.")
            return

        for product in products:
            try:
                # Scrape the latest price
                logger.info(f"'{product.name}' için güncel fiyat çekiliyor...")
                new_data = await url_service.extract_product(product.storeUrl)
                
                if new_data and new_data.currentPrice != product.currentPrice:
                    logger.info(f"Fiyat değişti! Eski: {product.currentPrice}, Yeni: {new_data.currentPrice}")
                    await repo.update_product_price(product.id, new_data.currentPrice)
                    
                    # Hedef fiyat kontrolü
                    if product.targetPrice and new_data.currentPrice <= product.targetPrice:
                        msg = f"🚨 {product.name} hedeflenen fiyata düştü: {new_data.currentPrice}"
                        # Sarı yazı, kırmızı arka plan için ANSI kodu
                        logger.info(f"\033[41;33m{msg}\033[0m")
                        await notif_repo.create_notification(product.id, msg)
                        # Sonsuz bildirimi engellemek için hedef fiyatı sıfırla
                        await repo.clear_target_price(product.id)
                else:
                    logger.info(f"'{product.name}' için fiyat değişikliği yok. (Güncel Fiyat: {product.currentPrice})")
            except Exception as e:
                logger.error(f"Ürün '{product.name}' güncellenirken hata oluştu: {e}")

scheduler = AsyncIOScheduler()
scheduler.add_job(update_prices_job, 'interval', minutes=1, id='update_prices_job', replace_existing=True)

def start_scheduler():
    scheduler.start()
    logger.info("APScheduler başlatıldı.")

def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler durduruldu.")
