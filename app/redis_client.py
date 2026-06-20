import traceback
from datetime import datetime
from typing import Optional
import redis.asyncio as redis
from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

async def set_key(key: str, value: str, expire_seconds: Optional[int] = None) -> None:
    """Set a key-value pair in Redis"""
    print(f"📝 REDIS SET: key={key}, value={value[:50] if value else None}, expire={expire_seconds}")
    await redis_client.set(key, value, ex=expire_seconds)
    print(f"✅ REDIS SET COMPLETE: {key}")

async def get_key(key: str) -> Optional[str]:
    """Get value by key"""
    print(f"🔍 REDIS GET: {key}")
    result = await redis_client.get(key)
    print(f"🔍 REDIS GET RESULT: {key} = {result}")
    return result

async def delete_key(key: str) -> None:
    """Delete a key"""
    print(f"🗑️ REDIS DELETE: {key}")
    await redis_client.delete(key)
    print(f"✅ REDIS DELETE COMPLETE: {key}")

async def exists_key(key: str) -> bool:
    """Check if key exists"""
    result = await redis_client.exists(key)
    print(f"🔍 REDIS EXISTS: {key} = {result > 0}")
    return result > 0

async def increment_key(key: str, expire_seconds: Optional[int] = None) -> int:
    """Increment a counter"""
    count = await redis_client.incr(key)
    print(f"📊 INCR: {key} = {count}")
    
    # Only set expiration on FIRST increment (count == 1)
    if expire_seconds and count == 1:
        await redis_client.expire(key, expire_seconds)
        print(f"⏰ EXPIRE SET: {key} for {expire_seconds}s")
    else:
        # Check current TTL (for debugging)
        ttl = await redis_client.ttl(key)
        print(f"⏰ Current TTL for {key}: {ttl}s")
    
    return count

async def blacklist_refresh_token(token: str, expires_in_days: int) -> None:
    """Add refresh token to blacklist"""
    key = f"blacklist:refresh:{token}"
    print(f"🚫 BLACKLIST REFRESH TOKEN: {key}")
    await set_key(key, "blacklisted", expires_in_days * 24 * 3600)

async def is_refresh_token_blacklisted(token: str) -> bool:
    """Check if refresh token is blacklisted"""
    key = f"blacklist:refresh:{token}"
    result = await exists_key(key)
    print(f"🔍 REFRESH TOKEN BLACKLISTED: {key} = {result}")
    return result

async def cache_short_url_with_ttl(short_code: str, original_url: str, ttl_seconds: int) -> None:
    """Cache URL mapping with custom TTL (seconds)"""
    key: str = f"url:{short_code}"
    print(f"💾 CACHE SHORT URL CALLED FOR: {short_code}")
    print(f"💾 Original URL: {original_url}")
    print(f"📍 Call stack for cache_short_url:")
    traceback.print_stack()
    await set_key(key, original_url, ttl_seconds)

async def cache_short_url(short_code: str, original_url: str, expire_seconds: int = 3600) -> None:
    """Cache URL mapping with default TTL 1 hour"""
    await cache_short_url_with_ttl(short_code, original_url, expire_seconds)


async def get_cached_url(short_code: str) -> Optional[str]:
    """Get cached URL"""
    key: str = f"url:{short_code}"
    print(f"🔍 GET CACHED URL CALLED FOR: {short_code}")
    value = await get_key(key)
    return value

async def invalidate_url_cache(short_code: str) -> None:
    """Remove URL from cache"""
    key = f"url:{short_code}"
    print(f"🗑️ INVALIDATE CACHE FOR: {short_code}")
    await delete_key(key)

async def close_redis() -> None:
    """Close Redis connection"""
    print(f"🔌 CLOSING REDIS CONNECTION")
    await redis_client.close()