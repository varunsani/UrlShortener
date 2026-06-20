from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.redis_client import increment_key
from app.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for API endpoints"""
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Skip rate limiting for docs and health
        if path == "/health" or path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        
        limit_key = None
        limit_value = None
        
        if path == "/api/urls/shorten" and request.method == "POST":
            limit_key = "create_url"
            limit_value = settings.rate_limit_create_url
        elif len(path.split("/")) == 2 and path != "/" and request.method == "GET":
            limit_key = "click_url"
            limit_value = settings.rate_limit_click_url
        
        if limit_key and limit_value:
            redis_key = f"rate_limit:{limit_key}:{client_ip}"
            current = await increment_key(redis_key, settings.rate_limit_window_seconds)
            
            print(f"📊 Rate Limit: {limit_key} - {current}/{limit_value} for {client_ip}")
            
            if current > limit_value:
                print(f"🚫 Rate limit exceeded - returning 429")
                # Option 1: Return response directly instead of raising exception
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": f"Rate limit exceeded. Max {limit_value} requests per {settings.rate_limit_window_seconds} seconds."}
                )
        
        return await call_next(request)