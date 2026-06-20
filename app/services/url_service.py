from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from app.models.url import URL
from app.models.analytics import Analytics
from app.utils.code_generator import generate_short_code
from app.redis_client import cache_short_url_with_ttl, get_cached_url, invalidate_url_cache

async def create_short_url(
    db: AsyncSession,
    original_url: str,
    user_id: int,
    expires_at: Optional[datetime] = None
) -> URL:
    # Generate unique short code
    while True:
        short_code = await generate_short_code()
        result = await db.execute(select(URL).where(URL.short_code == short_code))
        existing = result.scalar_one_or_none()
        if not existing:
            break
    
    url = URL(
        short_code=short_code,
        original_url=original_url,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(url)
    await db.commit()
    await db.refresh(url)
    
    # ✅ Cache with TTL equal to expiration time (or 1 hour if no expiration)
    if expires_at:
        # Calculate seconds until expiration
        now = datetime.now(timezone.utc)
        ttl_seconds = int((expires_at - now).total_seconds())
        if ttl_seconds > 0:
            await cache_short_url_with_ttl(short_code, original_url, ttl_seconds)
    else:
        # No expiration - cache for 1 hour
        await cache_short_url_with_ttl(short_code, original_url, 3600)
    
    return url

async def get_url_by_code(db: AsyncSession, short_code: str) -> Optional[URL]:
    """Get URL by short code with Redis cache"""
    
    current_time = datetime.now(timezone.utc)
    
    # Step 1: Try to get from cache
    cached_url = await get_cached_url(short_code)
    
    if cached_url:
        # Cache exists - but need to check if URL is still valid in DB
        result = await db.execute(
            select(URL.id, URL.clicks, URL.user_id, URL.expires_at, URL.is_active).where(
                URL.short_code == short_code
            )
        )
        db_data = result.first()
        
        if db_data:
            # Check if URL has expired in database
            if db_data.expires_at and db_data.expires_at < current_time:
                # URL expired - delete from cache
                await invalidate_url_cache(short_code)
                return None
            
            url = URL(
                id=db_data.id,
                short_code=short_code,
                original_url=cached_url,
                user_id=db_data.user_id,
                clicks=db_data.clicks,
                expires_at=db_data.expires_at,
                is_active=db_data.is_active
            )
            return url
        else:
            await invalidate_url_cache(short_code)
            return None
    
    # Step 2: Cache miss - get from database
    result = await db.execute(
        select(URL).where(URL.short_code == short_code, URL.is_active == True)
    )
    url = result.scalar_one_or_none()
    
    if not url:
        return None
    
    # Check if expired
    if url.expires_at and url.expires_at < current_time:
        return None
    
    # ✅ Cache with TTL equal to expiration time remaining
    if url.expires_at:
        ttl_seconds = int((url.expires_at - current_time).total_seconds())
        if ttl_seconds > 0:
            await cache_short_url_with_ttl(short_code, url.original_url, ttl_seconds)
    else:
        await cache_short_url_with_ttl(short_code, url.original_url, 3600)
    
    return url

async def increment_click_count(db: AsyncSession, url_id: int, short_code: str) -> None:
    """Increment click count and record analytics"""
    await db.execute(update(URL).where(URL.id == url_id).values(clicks=URL.clicks + 1))
    
    analytics = Analytics(url_id=url_id)
    db.add(analytics)
    await db.commit()
    
    # Invalidate cache so next request gets fresh data
    # await invalidate_url_cache(short_code)

async def get_user_urls(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[URL]:
    result = await db.execute(
        select(URL)
        .where(URL.user_id == user_id)
        .order_by(URL.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

async def get_url_by_id(
    db: AsyncSession,
    url_id: int,
    user_id: Optional[int] = None,
    is_admin: bool = False
) -> URL:
    result = await db.execute(select(URL).where(URL.id == url_id))
    url = result.scalar_one_or_none()
    
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if not is_admin and url.user_id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return url

async def delete_url(
    db: AsyncSession,
    url_id: int,
    user_id: Optional[int] = None,
    is_admin: bool = False
) -> None:
    url = await get_url_by_id(db, url_id, user_id, is_admin)
    url.is_active = False
    db.add(url)
    await db.commit()
    await invalidate_url_cache(url.short_code)

async def update_url(
    db: AsyncSession,
    url_id: int,
    user_id: int,
    original_url: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    is_active: Optional[bool] = None,
    is_admin: bool = False
) -> URL:
    url = await get_url_by_id(db, url_id, user_id, is_admin)
    
    if original_url:
        url.original_url = original_url
    if expires_at is not None:
        url.expires_at = expires_at
    if is_active is not None:
        url.is_active = is_active
    
    db.add(url)
    await db.commit()
    await db.refresh(url)
    await invalidate_url_cache(url.short_code)
    
    return url