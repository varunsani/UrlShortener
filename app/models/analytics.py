from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Analytics(Base):
    """Analytics model for tracking URL clicks"""
    __tablename__ = "analytics"
    
    id: int = Column(Integer, primary_key=True, index=True)
    url_id: int = Column(Integer, ForeignKey("urls.id"), nullable=False, index=True)
    clicked_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    url = relationship("URL", back_populates="analytics")