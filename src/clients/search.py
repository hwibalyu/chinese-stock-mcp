from __future__ import annotations

from src.clients.eastmoney_base import EastmoneyBaseClient
from src.settings import get_settings


class SearchClient(EastmoneyBaseClient):
    SEARCH_URL = "https://searchapi.eastmoney.com/api/suggest/get"

    async def search_stock(self, query: str, count: int = 10) -> dict:
        settings = get_settings()
        return await self.get_json(
            self.SEARCH_URL,
            params={
                "input": query,
                "type": 14,
                "token": settings.eastmoney_suggest_token,
                "count": count,
            },
        )
