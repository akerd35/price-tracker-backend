from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
import datetime
import uuid

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    store_url = Column(String, index=True)
    current_price = Column(Float)
    target_price = Column(Float, nullable=True)
    image_url = Column(String)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    
    notifications = relationship("Notification", back_populates="product", cascade="all, delete-orphan")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"))
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("Product", back_populates="notifications")
