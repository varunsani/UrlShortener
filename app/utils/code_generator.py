import random
import string
from app.config import settings

async def generate_short_code() -> str:
    """Generate random base62 short code"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choices(alphabet, k=settings.short_code_length))