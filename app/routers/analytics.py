from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_active_user, get_current_admin_user
from app.models.user import User, UserRole
from app.schemas.analytics import URLStats, AnalyticsSummary
from app.services import analytics_service
from app.services.url_service import get_user_urls

router: APIRouter = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/urls/{url_id}", response_model=URLStats)
async def get_url_analytics(
    url_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> URLStats:
    stats = await analytics_service.get_url_stats(
        db=db,
        url_id=url_id,
        is_admin=current_user.role == UserRole.ADMIN,
        user_id=current_user.id
    )
    return URLStats(**stats)

@router.get("/my-urls/summary", response_model=List[AnalyticsSummary])
async def get_my_urls_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[AnalyticsSummary]:
    urls = await get_user_urls(db, current_user.id)
    
    return [
        AnalyticsSummary(
            total_clicks=url.clicks,
            short_code=url.short_code,
            original_url=url.original_url
        )
        for url in urls
    ]

@router.get("/admin/all", response_model=List[AnalyticsSummary])
async def get_all_urls_analytics(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> List[AnalyticsSummary]:
    stats = await analytics_service.get_all_urls_stats(db, skip, limit)
    
    return [
        AnalyticsSummary(
            total_clicks=stat["total_clicks"],
            short_code=stat["short_code"],
            original_url=stat["original_url"]
        )
        for stat in stats
    ]