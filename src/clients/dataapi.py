from __future__ import annotations

from src.clients.eastmoney_base import EastmoneyBaseClient
from src.services.identifiers import build_identifier


class DataApiClient(EastmoneyBaseClient):
    MIXED_FEED_URL = "https://data.eastmoney.com/dataapi/stockdata/zxgg"

    async def get_mixed_feed(self, stock_code: str) -> dict:
        identifier = build_identifier(stock_code)
        return await self.get_json(
            self.MIXED_FEED_URL,
            params={"code": identifier.secid},
        )
