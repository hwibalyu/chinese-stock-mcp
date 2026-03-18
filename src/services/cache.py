from __future__ import annotations

from cachetools import TTLCache

from src.settings import get_settings

settings = get_settings()

quote_cache = TTLCache(maxsize=512, ttl=settings.quote_cache_ttl_seconds)
static_cache = TTLCache(maxsize=512, ttl=settings.static_cache_ttl_seconds)
notice_cache = TTLCache(maxsize=1024, ttl=settings.notice_cache_ttl_seconds)
