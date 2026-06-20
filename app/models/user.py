from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(50), unique=True, index=True, nullable=False)
    email: str = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(255), nullable=False)
    role: UserRole = Column(Enum(UserRole), default=UserRole.USER)
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    urls = relationship("URL", back_populates="user", cascade="all, delete-orphan")