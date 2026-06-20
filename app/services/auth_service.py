from typing import Optional
from datetime import datetime, timedelta
import bcrypt
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.config import settings
from app.models.user import User, UserRole

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt: bytes = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode: dict = data.copy()
    expire: datetime = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode: dict = data.copy()
    expire: datetime = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_token(token: str, token_type: str = "access") -> dict:
    """Decode and validate JWT token"""
    try:
        payload: dict = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def get_token_remaining_time(token: str, token_type: str = "refresh") -> int:
    """Get remaining seconds until token expires"""
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm],
            options={"verify_exp": False}  # Don't raise exception on expiry
        )
        exp = payload.get("exp")
        if exp:
            remaining = exp - int(datetime.utcnow().timestamp())
            return max(0, remaining)  # Don't return negative
    except:
        pass
    return 0  # Default to 0 if can't decode

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate user by username and password"""
    result = await db.execute(select(User).where(User.username == username))
    user: Optional[User] = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def create_admin_user(db: AsyncSession) -> None:
    """Create admin user if not exists"""
    result = await db.execute(select(User).where(User.username == settings.admin_username))
    admin: Optional[User] = result.scalar_one_or_none()
    
    if not admin:
        admin = User(
            username=settings.admin_username,
            email=settings.admin_email,
            hashed_password=hash_password(settings.admin_password),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print(f"Admin user created: {settings.admin_username}")