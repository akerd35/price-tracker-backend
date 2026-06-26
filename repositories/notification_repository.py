from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.db_models import Notification
from models.notification import NotificationResponse
import datetime

class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(self, product_id: str, message: str) -> NotificationResponse:
        new_notification = Notification(
            product_id=product_id,
            message=message,
            created_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        )
        self.db.add(new_notification)
        await self.db.commit()
        await self.db.refresh(new_notification)
        
        dt = new_notification.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
            
        return NotificationResponse(
            id=new_notification.id,
            product_id=new_notification.product_id,
            message=new_notification.message,
            is_read=new_notification.is_read,
            created_at=dt
        )

    async def get_all_notifications(self) -> list[NotificationResponse]:
        stmt = select(Notification).order_by(Notification.created_at.desc())
        result = await self.db.execute(stmt)
        db_notifications = result.scalars().all()
        
        notifications = []
        for n in db_notifications:
            dt = n.created_at
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            notifications.append(NotificationResponse(
                id=n.id,
                product_id=n.product_id,
                message=n.message,
                is_read=n.is_read,
                created_at=dt
            ))
        return notifications
