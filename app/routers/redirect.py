import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from app.database import get_db
from app.services import url_service
from app.models.url import URL

router = APIRouter(tags=["Redirect"])

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    db: AsyncSession = Depends(get_db)
) -> RedirectResponse:
    url = await url_service.get_url_by_code(db, short_code)
    
    if not url or not url.is_active:
        raise HTTPException(status_code=404, detail="Short URL not found or expired")
    
    # ✅ FIX: Use timezone-aware datetime comparison
    if url.expires_at and url.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="URL has expired")
    
    # AFTER getting URL and BEFORE returning, increment click count
    # But DO NOT invalidate cache - we want to keep the original_url cached
    await url_service.increment_click_count(db, url.id, short_code)
    
    return RedirectResponse(url=url.original_url, status_code=302)