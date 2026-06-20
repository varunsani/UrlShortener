from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class URLCreate(BaseModel):
    original_url: HttpUrl
    expires_at: Optional[datetime] = None

class URLResponse(BaseModel):
    id: int
    short_code: str
    original_url: str
    short_url: str
    clicks: int
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

class URLUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None