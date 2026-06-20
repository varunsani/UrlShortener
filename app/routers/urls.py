from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.url import URLCreate, URLResponse, URLUpdate
from app.services import url_service
from app.config import settings

router = APIRouter(prefix="/api/urls", tags=["URLs"])

@router.post("/shorten", response_model=URLResponse, status_code=201)
async def create_short_url(
    url_data: URLCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> URLResponse:
    url = await url_service.create_short_url(
        db=db,
        original_url=str(url_data.original_url),
        user_id=current_user.id,
        expires_at=url_data.expires_at
    )
    
    # ⚠️ Make sure there's NO cache_short_url call here
    
    return URLResponse(
        id=url.id,
        short_code=url.short_code,
        original_url=url.original_url,
        short_url=f"{settings.base_url}/{url.short_code}",
        clicks=url.clicks,
        created_at=url.created_at,
        expires_at=url.expires_at,
        is_active=url.is_active
    )

@router.get("/my-urls", response_model=List[URLResponse])
async def get_my_urls(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[URLResponse]:
    urls = await url_service.get_user_urls(db, current_user.id, skip, limit)
    
    return [
        URLResponse(
            id=url.id,
            short_code=url.short_code,
            original_url=url.original_url,
            short_url=f"{settings.base_url}/{url.short_code}",
            clicks=url.clicks,
            created_at=url.created_at,
            expires_at=url.expires_at,
            is_active=url.is_active
        )
        for url in urls
    ]

@router.get("/{url_id}", response_model=URLResponse)
async def get_url(
    url_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> URLResponse:
    url = await url_service.get_url_by_id(db, url_id, current_user.id, current_user.role == UserRole.ADMIN)
    
    return URLResponse(
        id=url.id,
        short_code=url.short_code,
        original_url=url.original_url,
        short_url=f"{settings.base_url}/{url.short_code}",
        clicks=url.clicks,
        created_at=url.created_at,
        expires_at=url.expires_at,
        is_active=url.is_active
    )

@router.put("/{url_id}", response_model=URLResponse)
async def update_url(
    url_id: int,
    url_data: URLUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> URLResponse:
    url = await url_service.update_url(
        db=db,
        url_id=url_id,
        user_id=current_user.id,
        original_url=str(url_data.original_url) if url_data.original_url else None,
        expires_at=url_data.expires_at,
        is_active=url_data.is_active,
        is_admin=current_user.role == UserRole.ADMIN
    )
    
    return URLResponse(
        id=url.id,
        short_code=url.short_code,
        original_url=url.original_url,
        short_url=f"{settings.base_url}/{url.short_code}",
        clicks=url.clicks,
        created_at=url.created_at,
        expires_at=url.expires_at,
        is_active=url.is_active
    )

@router.delete("/{url_id}", status_code=204)
async def delete_url(
    url_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> None:
    await url_service.delete_url(db, url_id, current_user.id, current_user.role == UserRole.ADMIN)
    return None