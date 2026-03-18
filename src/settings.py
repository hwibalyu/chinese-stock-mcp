from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CHINA_STOCK_", extra="ignore")

    app_name: str = "chinese-stock-mcp"
    eastmoney_suggest_token: str = Field(
        default="D43BF722C8E33BDC906FB84D85E326E8"
    )
    eastmoney_xuangu_fingerprint: str = Field(
        default="6d09ac0e7326d9299bb77ac2090dadd9"
    )
    http_timeout_seconds: float = 15.0
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    )
    quote_cache_ttl_seconds: int = 30
    static_cache_ttl_seconds: int = 3600
    notice_cache_ttl_seconds: int = 86400


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
