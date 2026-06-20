from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException
from app.models.url import URL
from app.models.analytics import Analytics

async def get_url_stats(
    db: AsyncSession,
    url_id: int,
    is_admin: bool = False,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    result = await db.execute(select(URL).where(URL.id == url_id))
    url: Optional[URL] = result.scalar_one_or_none()
    
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if not is_admin and url.user_id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    recent_result = await db.execute(
        select(Analytics)
        .where(Analytics.url_id == url_id)
        .order_by(Analytics.clicked_at.desc())
        .limit(10)
    )
    recent_clicks = list(recent_result.scalars().all())
    
    daily: Dict[str, int] = await get_daily_breakdown(db, url_id)
    weekly: Dict[str, int] = await get_weekly_breakdown(db, url_id)
    monthly: Dict[str, int] = await get_monthly_breakdown(db, url_id)
    
    return {
        "short_code": url.short_code,
        "total_clicks": url.clicks,
        "recent_clicks": [
            {
                "url_id": click.url_id,
                "short_code": url.short_code,
                "clicked_at": click.clicked_at
            }
            for click in recent_clicks
        ],
        "breakdown": {"daily": daily, "weekly": weekly, "monthly": monthly}
    }

async def get_daily_breakdown(db: AsyncSession, url_id: int) -> Dict[str, int]:
    cutoff_date: datetime = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(
            func.date(Analytics.clicked_at).label("day"),
            func.count(Analytics.id).label("count")
        )
        .where(and_(Analytics.url_id == url_id, Analytics.clicked_at >= cutoff_date))
        .group_by(func.date(Analytics.clicked_at))
        .order_by(func.date(Analytics.clicked_at))
    )
    return {str(row.day): row.count for row in result.all()}

async def get_weekly_breakdown(db: AsyncSession, url_id: int) -> Dict[str, int]:
    cutoff_date: datetime = datetime.now(timezone.utc) - timedelta(weeks=12)
    result = await db.execute(
        select(
            func.date_trunc('week', Analytics.clicked_at).label('week'),
            func.count(Analytics.id).label('count')
        )
        .where(and_(Analytics.url_id == url_id, Analytics.clicked_at >= cutoff_date))
        .group_by('week')
        .order_by('week')
    )
    return {str(row.week.date()): row.count for row in result.all()}

async def get_monthly_breakdown(db: AsyncSession, url_id: int) -> Dict[str, int]:
    cutoff_date: datetime = datetime.now(timezone.utc) - timedelta(days=365)
    result = await db.execute(
        select(
            func.date_trunc('month', Analytics.clicked_at).label('month'),
            func.count(Analytics.id).label('count')
        )
        .where(and_(Analytics.url_id == url_id, Analytics.clicked_at >= cutoff_date))
        .group_by('month')
        .order_by('month')
    )
    return {str(row.month.date()): row.count for row in result.all()}

async def get_all_urls_stats(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(URL)
        .where(URL.is_active == True)
        .order_by(URL.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    urls = list(result.scalars().all())
    
    return [
        {
            "short_code": url.short_code,
            "original_url": url.original_url,
            "total_clicks": url.clicks,
            "user_id": url.user_id,
            "created_at": url.created_at
        }
        for url in urls
    ]