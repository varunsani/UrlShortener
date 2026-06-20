from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token, TokenRefresh, UserResponse
from app.services.auth_service import (
    hash_password, create_access_token, create_refresh_token, 
    decode_token, authenticate_user, get_token_remaining_time
)
from app.dependencies.auth import get_current_user
from app.redis_client import blacklist_refresh_token, is_refresh_token_blacklisted
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user: User = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse.model_validate(new_user)

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    user: User = await authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    

    access_token: str = create_access_token({"sub": str(user.id)})
    refresh_token: str = create_refresh_token({"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
) -> Token:
    # Check if token is blacklisted (already used or logged out)
    if await is_refresh_token_blacklisted(refresh_data.refresh_token):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    payload = decode_token(refresh_data.refresh_token, "refresh")
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    remaining_seconds = get_token_remaining_time(refresh_data.refresh_token, "refresh")

    # Create NEW tokens (both access and refresh)
    new_access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # ✅ BLACKLIST the OLD refresh token (so it can't be used again)
    if remaining_seconds > 0:
        await blacklist_refresh_token(refresh_data.refresh_token, remaining_seconds // 86400)
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )

@router.post("/logout", status_code=204)
async def logout(
    refresh_data: TokenRefresh,
    current_user: User = Depends(get_current_user)
) -> None:
    remaining_seconds = get_token_remaining_time(refresh_data.refresh_token, "refresh")
    if remaining_seconds > 0:
        await blacklist_refresh_token(refresh_data.refresh_token, remaining_seconds // 86400)
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return UserResponse.model_validate(current_user)