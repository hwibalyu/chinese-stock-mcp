from __future__ import annotations

from time import time

from src.clients.eastmoney_base import EastmoneyBaseClient
from src.settings import get_settings


class XuanguClient(EastmoneyBaseClient):
    SEARCH_CODE_URL = "https://np-tjxg-g.eastmoney.com/api/smart-tag/stock/v3/pw/search-code"

    def __init__(self) -> None:
        super().__init__()
        self._client.headers.update(
            {
                "Origin": "https://xuangu.eastmoney.com",
                "Referer": "https://xuangu.eastmoney.com/",
            }
        )

    async def screen_stocks(self, query: str, page_no: int = 1, page_size: int = 20) -> dict:
        settings = get_settings()
        now_ms = str(int(time() * 1000))
        return await self.post_json(
            self.SEARCH_CODE_URL,
            payload={
                "KeyWord": query,
                "pageSize": page_size,
                "pageNo": page_no,
                "Fingerprint": settings.eastmoney_xuangu_fingerprint,
                "MatchWord": "",
                "ShareToGuba": False,
                "Timestamp": now_ms,
                "RequestID": f"chinese-stock-mcp-{now_ms}",
                "RemovedConditionIDList": [],
                "OwnSelectAll": False,
                "NeedCorrect": True,
                "Client": "web",
                "DxInfo": [],
                "Biz": "web_ai_select_stocks",
                "Gids": [],
            },
        )
