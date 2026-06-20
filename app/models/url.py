from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class URL(Base):
    """URL model for shortened links"""
    __tablename__ = "urls"
    
    id: int = Column(Integer, primary_key=True, index=True)
    short_code: str = Column(String(12), unique=True, index=True, nullable=False)
    original_url: str = Column(String(2048), nullable=False)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    clicks: int = Column(BigInteger, default=0)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    expires_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    is_active: bool = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="urls")
    analytics = relationship("Analytics", back_populates="url", cascade="all, delete-orphan")