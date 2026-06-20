from typing import Dict, List
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, urls, analytics, redirect
from app.middleware.rate_limit import RateLimitMiddleware
from app.database import get_db
from app.services.auth_service import create_admin_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup - Create admin user if not exists
    print("Checking for admin user...")
    async for db in get_db():
        await create_admin_user(db)
        break
    print("Admin user setup complete")
    print(f"Application started at {settings.base_url}")
    yield
    # Shutdown - Clean up if needed
    print("Shutting down...")

app = FastAPI(
    title=settings.app_name, 
    version="1.0.0",
    lifespan=lifespan
)

# Convert comma-separated string to list
allowed_origins_list: List[str] = [origin.strip() for origin in settings.allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "URL Shortener API", "docs": "/docs", "base_url": settings.base_url}

@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}



app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(analytics.router)
app.include_router(redirect.router)